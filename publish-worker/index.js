// Decommissioned. The publish run is finished; this stub refuses every request
// and holds no R2 binding. Safe to delete the worker (novel-publisher) entirely.
export default {
  async fetch() {
    return new Response("gone", { status: 410 });
  },
};
