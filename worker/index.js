// Cloudflare Worker entry. Every request passes the sign-in and lock checks before a file is served.
import { onRequest as guard } from '../lib/guard.js';
import { onRequestGet as apiMe } from '../lib/me.js';
import { onPost as apiPlatform } from '../lib/platform.js';

export default {
  async fetch(request, env) {
    const data = {};
    const next = async () => {
      const path = new URL(request.url).pathname;
      if (path === '/api/me') {
        if (request.method !== 'GET') return new Response('Method not allowed', { status: 405 });
        return apiMe({ request, env, data });
      }
      if (path === '/api/quiz' || path === '/api/hint') {
        if (request.method !== 'POST') return new Response('Method not allowed', { status: 405 });
        return apiPlatform({ request, env, data }, path);
      }
      if (path.startsWith('/api/')) return new Response('Not found', { status: 404 });
      return env.ASSETS.fetch(request);
    };
    return guard({ request, env, data, next });
  },
};
