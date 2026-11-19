export default {
  async fetch() {
    return new Response("gone", { status: 410 });
  },
};
