import type { APIRoute } from 'astro';
import { env as cfEnv } from 'cloudflare:workers';

const RATE_LIMIT_PER_MINUTE = 3;
const RATE_WINDOW_SEC = 60;
const TIMESTAMP_TOLERANCE_MS = 10_000;
const MAX_CONTENT_LENGTH = 1000;

interface KVNamespaceLike {
  get(key: string): Promise<string | null>;
  put(key: string, value: string, options?: { expirationTtl?: number }): Promise<void>;
}

interface Env {
  FEISHU_WEBHOOK_URL?: string;
  FEISHU_APP_ID?: string;
  FEISHU_APP_SECRET?: string;
  FEISHU_RECEIVE_ID?: string;
  FEISHU_RECEIVE_ID_TYPE?: string;
  FEISHU_ADMIN_OPEN_ID?: string;
  SESSION?: KVNamespaceLike;
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

async function checkRateLimit(ipHash: string, kv: KVNamespaceLike | undefined): Promise<boolean> {
  if (!kv) return true;
  const key = `feedback_rate:${ipHash}`;
  const now = Math.floor(Date.now() / 1000);
  const windowStart = Math.floor(now / RATE_WINDOW_SEC) * RATE_WINDOW_SEC;

  try {
    const raw = await kv.get(key);
    const record = raw ? (JSON.parse(raw) as { windowStart: number; count: number }) : null;
    if (record && record.windowStart === windowStart) {
      if (record.count >= RATE_LIMIT_PER_MINUTE) return false;
      record.count += 1;
      await kv.put(key, JSON.stringify(record), { expirationTtl: RATE_WINDOW_SEC + 1 });
    } else {
      await kv.put(key, JSON.stringify({ windowStart, count: 1 }), { expirationTtl: RATE_WINDOW_SEC + 1 });
    }
  } catch {
    return true;
  }
  return true;
}

async function getTenantAccessToken(env: Env): Promise<string | null> {
  const appId = env.FEISHU_APP_ID;
  const appSecret = env.FEISHU_APP_SECRET;
  if (!appId || !appSecret) return null;

  const cacheKey = 'feishu_token';
  if (env.SESSION) {
    try {
      const cached = await env.SESSION.get(cacheKey);
      if (cached) {
        const { token, expires_at } = JSON.parse(cached) as { token: string; expires_at: number };
        if (Date.now() < expires_at - 60_000) return token;
      }
    } catch {}
  }

  try {
    const res = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ app_id: appId, app_secret: appSecret }),
    });
    const data = await res.json();
    if (data?.code !== 0 || !data.tenant_access_token) return null;

    const token = data.tenant_access_token as string;
    const expire = Number(data.expire || 7200);
    if (env.SESSION) {
      await env.SESSION.put(
        cacheKey,
        JSON.stringify({ token, expires_at: Date.now() + expire * 1000 }),
        { expirationTtl: expire }
      );
    }
    return token;
  } catch {
    return null;
  }
}

async function sendViaBot(env: Env, message: string): Promise<{ ok: boolean; error?: string }> {
  const token = await getTenantAccessToken(env);
  if (!token) return { ok: false, error: 'Failed to get Feishu token' };

  let receiveId = env.FEISHU_RECEIVE_ID;
  let receiveType = env.FEISHU_RECEIVE_ID_TYPE || 'open_id';

  // Fallback to admin open_id captured by event endpoint
  if (!receiveId && env.SESSION) {
    try {
      const raw = await env.SESSION.get('feishu_admin_open_id');
      if (raw) {
        const parsed = JSON.parse(raw) as { open_id?: string; chat_id?: string };
        receiveId = parsed.open_id || parsed.chat_id || '';
        if (parsed.chat_id && !parsed.open_id) receiveType = 'chat_id';
      }
    } catch {}
  }

  if (!receiveId) return { ok: false, error: 'No recipient configured' };

  try {
    const res = await fetch(
      `https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=${receiveType}`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          receive_id: receiveId,
          msg_type: 'text',
          content: JSON.stringify({ text: message }),
        }),
      }
    );
    const data = await res.json();
    if (data?.code !== 0) return { ok: false, error: data?.msg || 'Feishu API error' };
    return { ok: true };
  } catch (err: any) {
    return { ok: false, error: err.message || 'Network error' };
  }
}

async function sendViaWebhook(url: string, message: string): Promise<{ ok: boolean; error?: string }> {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        msg_type: 'text',
        content: { text: message },
      }),
    });
    const data = await res.json().catch(async () => ({ status: await res.text() }));
    if (!res.ok) return { ok: false, error: JSON.stringify(data) };
    return { ok: true };
  } catch (err: any) {
    return { ok: false, error: err.message || 'Network error' };
  }
}

export const OPTIONS: APIRoute = async ({ request }) => {
  const origin = request.headers.get('origin') || '*';
  return new Response(null, { status: 204, headers: corsHeaders(origin) });
};

export const POST: APIRoute = async ({ request }) => {
  const origin = request.headers.get('origin') || '*';
  const headers = { ...corsHeaders(origin), 'Content-Type': 'application/json' };
  const env = getEnv();

  const hasWebhook = !!env.FEISHU_WEBHOOK_URL;
  const hasBotCreds = !!env.FEISHU_APP_ID && !!env.FEISHU_APP_SECRET;

  if (!hasWebhook && !hasBotCreds) {
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

  const message = `📢 Reader Feedback\n👤 User: ${safeUser}\n📖 Chapter: ${safeChapter}\n💬 Message: ${safeContent}\n🔗 URL: ${safeUrl}\n📱 UA: ${safeUA}\n🌐 IP: ${ip}`;

  let result: { ok: boolean; error?: string };
  if (hasWebhook) {
    result = await sendViaWebhook(env.FEISHU_WEBHOOK_URL!, message);
  } else {
    result = await sendViaBot(env, message);
  }

  if (!result.ok) {
    return new Response(JSON.stringify({ success: false, error: result.error }), { status: 502, headers });
  }

  return new Response(JSON.stringify({ success: true }), { status: 200, headers });
};

export const GET: APIRoute = async ({ request }) => {
  const origin = request.headers.get('origin') || '*';
  return new Response(JSON.stringify({ ok: true, message: 'Use POST to submit feedback' }), {
    status: 405,
    headers: { ...corsHeaders(origin), 'Content-Type': 'application/json' },
  });
};
