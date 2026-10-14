// Cloudflare Worker entry. Every request passes the sign-in and lock checks before a file is served.
import { onRequest as guard } from '../lib/guard.js';
import { onRequestGet as apiMe } from '../lib/me.js';

export default {
  async fetch(request, env) {
    const data = {};
    const next = async () => {
      const path = new URL(request.url).pathname;
      if (path === '/api/me') {
        if (request.method !== 'GET') return new Response('Method not allowed', { status: 405 });
        return apiMe({ request, env, data });
      }
      return env.ASSETS.fetch(request);
    };
    return guard({ request, env, data, next });
  },
};
