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
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

export const OPTIONS: APIRoute = async ({ request }) => {
  const origin = request.headers.get('origin') || '*';
  return new Response(null, { status: 204, headers: corsHeaders(origin) });
};

export const POST: APIRoute = async ({ request }) => {
  const headers = { 'Content-Type': 'application/json' };
  const env = getEnv();

  let body: any;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), { status: 400, headers });
  }

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

      // Reply with confirmation if user asks for their id
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

export const GET: APIRoute = async () => {
  const env = getEnv();
  let stored = null;
  try {
    stored = env.SESSION ? await env.SESSION.get('feishu_admin_open_id') : null;
  } catch {
    stored = null;
  }
  return new Response(
    JSON.stringify({ ok: true, has_open_id: !!stored, detail: stored ? JSON.parse(stored) : null }),
    { status: 200, headers: { 'Content-Type': 'application/json' } }
  );
};
