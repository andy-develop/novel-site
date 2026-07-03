import type { APIRoute } from 'astro';
import { env as cfEnv } from 'cloudflare:workers';

const RATE_LIMIT_PER_MINUTE = 3;
const RATE_WINDOW_SEC = 60;
const TIMESTAMP_TOLERANCE_MS = 10_000;
const MAX_CONTENT_LENGTH = 1000;

interface Env {
  FEISHU_WEBHOOK_URL?: string;
  SESSION?: KVNamespace;
}

function getEnv(): Env {
  return (cfEnv as Record<string, any>) as Env;
}

function getClientIP(request: Request): string {
  return (
    request.headers.get('cf-connecting-ip') ||
    request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ||
    'unknown'
  );
}

function hashIp(ip: string): string {
  let h = 0;
  for (let i = 0; i < ip.length; i++) {
    h = ((h << 5) - h + ip.charCodeAt(i)) | 0;
  }
  return 'fb_' + Math.abs(h).toString(36);
}

function corsHeaders(origin = '*'): Record<string, string> {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

async function checkRateLimit(ipHash: string, kv: KVNamespace | undefined): Promise<boolean> {
  if (!kv) return true; // no KV = no rate limit (should not happen in production)
  const key = `feedback_rate:${ipHash}`;
  const now = Math.floor(Date.now() / 1000);
  const windowStart = Math.floor(now / RATE_WINDOW_SEC) * RATE_WINDOW_SEC;

  try {
    const raw = await kv.get(key);
    const record = raw ? JSON.parse(raw) as { windowStart: number; count: number } : null;
    if (record && record.windowStart === windowStart) {
      if (record.count >= RATE_LIMIT_PER_MINUTE) return false;
      record.count += 1;
      await kv.put(key, JSON.stringify(record), { expirationTtl: RATE_WINDOW_SEC + 1 });
    } else {
      await kv.put(key, JSON.stringify({ windowStart, count: 1 }), { expirationTtl: RATE_WINDOW_SEC + 1 });
    }
  } catch {
    // Fail open on KV errors so feedback isn't lost due to infra issues
    return true;
  }
  return true;
}

export const OPTIONS: APIRoute = async ({ request }) => {
  const origin = request.headers.get('origin') || '*';
  return new Response(null, { status: 204, headers: corsHeaders(origin) });
};

export const POST: APIRoute = async ({ request }) => {
  const origin = request.headers.get('origin') || '*';
  const headers = { ...corsHeaders(origin), 'Content-Type': 'application/json' };
  const env = getEnv();
  const webhookUrl = env.FEISHU_WEBHOOK_URL;

  if (!webhookUrl) {
    return new Response(JSON.stringify({ success: false, error: 'Feedback service not configured' }), {
      status: 503,
      headers,
    });
  }

  let body: any;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ success: false, error: 'Invalid JSON' }), { status: 400, headers });
  }

  const { user, content, currentUrl, chapter, ua, timestamp } = body;

  // Anti-replay / anti-stale timestamp
  const ts = Number(timestamp);
  if (!timestamp || Number.isNaN(ts) || Math.abs(Date.now() - ts) > TIMESTAMP_TOLERANCE_MS) {
    return new Response(JSON.stringify({ success: false, error: 'Invalid request timestamp' }), { status: 403, headers });
  }

  if (!content || typeof content !== 'string' || content.trim().length < 3) {
    return new Response(JSON.stringify({ success: false, error: 'Feedback content too short' }), { status: 400, headers });
  }

  if (content.length > MAX_CONTENT_LENGTH) {
    return new Response(JSON.stringify({ success: false, error: `Feedback too long (max ${MAX_CONTENT_LENGTH})` }), { status: 400, headers });
  }

  if (!currentUrl || typeof currentUrl !== 'string') {
    return new Response(JSON.stringify({ success: false, error: 'Missing page URL' }), { status: 400, headers });
  }

  const ip = getClientIP(request);
  const ipHash = hashIp(ip);
  const allowed = await checkRateLimit(ipHash, env.SESSION);
  if (!allowed) {
    return new Response(JSON.stringify({ success: false, error: 'Rate limit exceeded, please try later' }), { status: 429, headers });
  }

  const safeContent = content.trim();
  const safeChapter = typeof chapter === 'string' ? chapter : 'Unknown';
  const safeUser = typeof user === 'string' && user.trim() ? user.trim() : 'Guest';
  const safeUrl = currentUrl.length > 500 ? currentUrl.slice(0, 500) : currentUrl;
  const safeUA = typeof ua === 'string' ? ua.slice(0, 300) : 'Unknown';

  const feishuPayload = {
    msg_type: 'text',
    content: {
      text: `📢 Reader Feedback\n👤 User: ${safeUser}\n📖 Chapter: ${safeChapter}\n💬 Message: ${safeContent}\n🔗 URL: ${safeUrl}\n📱 UA: ${safeUA}\n🌐 IP: ${ip}`,
    },
  };

  try {
    const feishuResponse = await fetch(webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(feishuPayload),
    });

    const result = await feishuResponse.json().catch(async () => ({ status: await feishuResponse.text() }));

    if (!feishuResponse.ok) {
      return new Response(JSON.stringify({ success: false, error: 'Failed to forward feedback', detail: result }), {
        status: 502,
        headers,
      });
    }

    return new Response(JSON.stringify({ success: true, result }), { status: 200, headers });
  } catch (err: any) {
    return new Response(JSON.stringify({ success: false, error: err.message || 'Network error' }), { status: 500, headers });
  }
};

export const GET: APIRoute = async ({ request }) => {
  const origin = request.headers.get('origin') || '*';
  return new Response(JSON.stringify({ ok: true, message: 'Use POST to submit feedback' }), {
    status: 405,
    headers: { ...corsHeaders(origin), 'Content-Type': 'application/json' },
  });
};
