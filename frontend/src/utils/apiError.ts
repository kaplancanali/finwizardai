import axios from 'axios';
import { getEffectiveApiBase } from '../services/api';

const PROD_MISSING_API_HINT =
  'API sunucusuna ulaşılamıyor. Statik sitede /api/v1 yolu yok; FastAPI backend ayrı çalışmalı.\n\n' +
  'Çözüm (birini yapın):\n' +
  '• Vercel + ayrı backend: Proje kökündeki api/[...path].js proxy kullanır. Vercel → Settings → Environment Variables → FINVIS_BACKEND_URL = https://senin-fastapi.up.railway.app (sadece origin, sonda / yok). Redeploy.\n' +
  '• Tek sunucu: backend’de SERVE_SPA=true, nginx/Caddy ile tek porta yönlendirin (README).\n' +
  '• Veya frontend/public/api-config.json içinde "apiBase": "https://.../api/v1" veya build’de VITE_API_URL.';

export function formatApiError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const status = err.response?.status;
    const relativeApi = getEffectiveApiBase().startsWith('/');
    if (import.meta.env.PROD && relativeApi && status === 404) {
      return `${PROD_MISSING_API_HINT}\n\n(Teknik: ${err.message})`;
    }
    return err.message || 'İstek başarısız';
  }
  if (err instanceof Error) return err.message;
  return 'Bir hata oluştu';
}
