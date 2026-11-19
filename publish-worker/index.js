// Temporary upload endpoint for the novel-data R2 bucket.
// Deployed by .github/workflows/publish-novel.yml because the repo's
// CLOUDFLARE_API_TOKEN is scoped for Workers deploy only, not R2 API.
// Guarded by a bearer key; deleted after the publish run.

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.headers.get("x-publish-key") !== env.PUBLISH_KEY) {
      return new Response("forbidden", { status: 403 });
    }
    const key = url.searchParams.get("key");

    if (request.method === "GET") {
      if (url.searchParams.get("list") !== null) {
        const listed = await env.R2_BUCKET.list({ prefix: url.searchParams.get("list") || "", limit: 1000 });
        return Response.json({ keys: listed.objects.map((o) => ({ key: o.key, size: o.size, uploaded: o.uploaded })) });
      }
      if (!key) return new Response("key required", { status: 400 });
      const head = await env.R2_BUCKET.head(key);
      if (!head) return new Response("missing", { status: 404 });
      return Response.json({ key, size: head.size, uploaded: head.uploaded, cacheControl: head.httpMetadata && head.httpMetadata.cacheControl });
    }

    if (request.method === "PUT" || request.method === "POST") {
      if (!key) return new Response("key required", { status: 400 });
      const body = await request.arrayBuffer();
      const cc = url.searchParams.get("cc") || "public, max-age=31536000, immutable";
      await env.R2_BUCKET.put(key, body, {
        httpMetadata: { contentType: "application/json", cacheControl: cc },
      });
      return Response.json({ ok: true, key, bytes: body.byteLength, cacheControl: cc });
    }

    return new Response("method not allowed", { status: 405 });
  },
};