import axios from 'axios';
import { getEffectiveApiBase } from '../services/api';

const PROD_MISSING_API_HINT =
  'API sunucusuna ulaşılamıyor. Statik sitede /api/v1 yolu yok; FastAPI backend ayrı çalışmalı.\n\n' +
  'Çözüm (birini yapın):\n' +
  '1) frontend/public/api-config.json içinde "apiBase" alanına backend adresini yazın, örn. "https://xxx.railway.app/api/v1" (sonda / olmasın), commit + deploy.\n' +
  '2) Veya host panelinde VITE_API_URL ile aynı adresi build ortamına verip yeniden derleyin.\n' +
  '3) Veya aynı domainde /api isteğini reverse proxy ile backend’e yönlendirin.';

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
