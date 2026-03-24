import axios from 'axios';

const PROD_MISSING_API_HINT =
  'API sunucusuna ulaşılamıyor. Statik sitede /api/v1 yolu yok; FastAPI backend ayrı çalışmalı. ' +
  'Host panelinde (Vercel vb.) derleme ortamına VITE_API_URL ekleyin — tam taban, örn. https://api.siteniz.com/api/v1 ' +
  '(sonda / olmasın). Ardından projeyi yeniden derleyip yayınlayın. İsterseniz aynı domainde /api isteğini reverse proxy ile backend’e yönlendirin.';

export function formatApiError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const status = err.response?.status;
    const hasApiBase = Boolean(
      import.meta.env.VITE_API_URL &&
        String(import.meta.env.VITE_API_URL).trim().length > 0
    );
    if (import.meta.env.PROD && !hasApiBase && status === 404) {
      return `${PROD_MISSING_API_HINT}\n\n(Teknik: ${err.message})`;
    }
    return err.message || 'İstek başarısız';
  }
  if (err instanceof Error) return err.message;
  return 'Bir hata oluştu';
}
