/**
 * Vercel Serverless: /api/* isteklerini gerçek FastAPI sunucusuna iletir.
 *
 * Vercel proje ayarlarında Environment Variable:
 *   FINVIS_BACKEND_URL=https://senin-backend.up.railway.app
 * (sadece origin; sonda / yok, /api ekleme — kod /api/v1/... ekler)
 */
module.exports = async function handler(req, res) {
  const backend = process.env.FINVIS_BACKEND_URL;
  if (!backend || !String(backend).trim()) {
    res.status(503).setHeader('Content-Type', 'application/json');
    res.end(
      JSON.stringify({
        detail:
          'Vercel ortamında FINVIS_BACKEND_URL tanımlı değil. Railway/Render vb. FastAPI adresini bu değişkene yazın (örn. https://xxx.up.railway.app).',
      })
    );
    return;
  }

  const origin = String(backend).replace(/\/$/, '');
  const segments = req.query.path;
  const sub = Array.isArray(segments) ? segments.join('/') : segments || '';
  const q = req.url && req.url.includes('?') ? req.url.slice(req.url.indexOf('?')) : '';
  const targetUrl = `${origin}/api/${sub}${q}`;

  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', req.headers['access-control-request-headers'] || 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }

  const hop = ['connection', 'content-length', 'host', 'transfer-encoding'];
  const headers = {};
  for (const [k, v] of Object.entries(req.headers)) {
    if (!v || hop.includes(k.toLowerCase())) continue;
    headers[k] = v;
  }

  try {
    let body;
    if (!['GET', 'HEAD'].includes(req.method) && req.body !== undefined && req.body !== null) {
      body = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
    }

    const init = {
      method: req.method,
      headers,
      redirect: 'manual',
    };
    if (body !== undefined) init.body = body;

    const r = await fetch(targetUrl, init);

    const ct = r.headers.get('content-type');
    if (ct) res.setHeader('Content-Type', ct);

    const buf = Buffer.from(await r.arrayBuffer());
    res.status(r.status).send(buf);
  } catch (e) {
    res.status(502).setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ detail: 'Proxy hatası', message: String(e && e.message ? e.message : e) }));
  }
};
