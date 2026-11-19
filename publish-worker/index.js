// Decommissioned. This endpoint was a temporary R2 writer for one publish run.
export default {
  async fetch() {
    return new Response("gone", { status: 410 });
  },
};
