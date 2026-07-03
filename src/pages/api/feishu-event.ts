import type { APIRoute } from 'astro';
import { env as cfEnv } from 'cloudflare:workers';

interface KVNamespaceLike {
  get(key: string): Promise<string | null>;
  put(key: string, value: string, options?: { expirationTtl?: number }): Promise<void>;
}

interface Env {
  SESSION?: KVNamespaceLike;
  FEISHU_VERIFICATION_TOKEN?: string;
}

function getEnv(): Env {
  return (cfEnv as Record<string, any>) as Env;
}

function corsHeaders(origin = '*'): Record<string, string> {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS, GET',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

async function logRequest(env: Env, label: string, request: Request, extra?: any) {
  if (!env.SESSION) return;
  try {
    const bodyText = await request.clone().text();
    const log = {
      label,
      time: new Date().toISOString(),
      method: request.method,
      url: request.url,
      headers: Object.fromEntries(request.headers.entries()),
      bodyText,
      extra,
    };
    await env.SESSION.put(
      `feishu_event_log:${Date.now()}:${label}`,
      JSON.stringify(log),
      { expirationTtl: 86400 }
    );
  } catch {}
}

export const OPTIONS: APIRoute = async ({ request }) => {
  const origin = request.headers.get('origin') || '*';
  return new Response(null, { status: 204, headers: corsHeaders(origin) });
};

export const POST: APIRoute = async ({ request }) => {
  const env = getEnv();
  const headers = { 'Content-Type': 'application/json' };

  // Always log the raw request first
  await logRequest(env, 'raw_post', request);

  let bodyText = '';
  try {
    bodyText = await request.text();
  } catch {
    bodyText = '';
  }

  // Try to parse JSON very defensively
  let body: any = {};
  try {
    body = bodyText ? JSON.parse(bodyText) : {};
  } catch {
    await logRequest(env, 'json_parse_error', request, { bodyText });
    // Even if JSON parse fails, try to echo any challenge pattern in the raw text
    const challengeMatch = bodyText.match(/"challenge"\s*:\s*"([^"]+)"/);
    if (challengeMatch) {
      return new Response(JSON.stringify({ challenge: challengeMatch[1] }), { status: 200, headers });
    }
    return new Response(JSON.stringify({ error: 'Invalid JSON', received: bodyText.slice(0, 500) }), { status: 400, headers });
  }

  await logRequest(env, 'parsed', request, { body });

  // URL verification challenge
  if (body?.type === 'url_verification') {
    return new Response(JSON.stringify({ challenge: body.challenge }), { status: 200, headers });
  }

  // Optional: verify token from Feishu console
  const token = env.FEISHU_VERIFICATION_TOKEN;
  if (token && body?.token !== token) {
    return new Response(JSON.stringify({ error: 'Invalid token' }), { status: 403, headers });
  }

  // Capture user open_id from messages sent to the bot
  if (body?.type === 'event_callback') {
    const event = body.event || {};
    if (event?.type === 'im.message.receive_v1') {
      const sender = event.sender?.sender_id;
      const openId = sender?.open_id;
      const userId = sender?.user_id;
      const chatId = event.message?.chat_id;
      let text = '';
      try {
        text = event.message?.content ? JSON.parse(event.message.content)?.text : '';
      } catch {}

      if (openId && env.SESSION) {
        await env.SESSION.put(
          'feishu_admin_open_id',
          JSON.stringify({ open_id: openId, user_id: userId, chat_id: chatId, updated_at: Date.now() }),
          { expirationTtl: 86400 * 30 }
        );
      }

      const lower = String(text || '').toLowerCase();
      if (lower.includes('open_id') || lower.includes('id')) {
        return new Response(
          JSON.stringify({
            challenge: '',
            reply: `你的 open_id 是：${openId}\nchat_id 是：${chatId}`,
          }),
          { status: 200, headers }
        );
      }
    }
  }

  return new Response(JSON.stringify({ challenge: '' }), { status: 200, headers });
};

export const GET: APIRoute = async ({ request }) => {
  const env = getEnv();
  const url = new URL(request.url);
  const challenge = url.searchParams.get('challenge');

  // Feishu sometimes probes with GET before POST verification
  if (challenge) {
    return new Response(JSON.stringify({ challenge }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  let stored = null;
  let logs: string[] = [];
  try {
    stored = env.SESSION ? await env.SESSION.get('feishu_admin_open_id') : null;
    if (env.SESSION) {
      const list = await env.SESSION.list({ prefix: 'feishu_event_log:' });
      logs = list.keys.map((k) => k.name).slice(-20);
    }
  } catch {
    stored = null;
  }
  return new Response(
    JSON.stringify({ ok: true, has_open_id: !!stored, detail: stored ? JSON.parse(stored) : null, recent_logs: logs }),
    { status: 200, headers: { 'Content-Type': 'application/json' } }
  );
};
