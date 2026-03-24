# FinVis Frontend

Modern React + TypeScript + Tailwind CSS arayüzü.

## Özellikler

- Modern ve kullanıcı dostu tasarım
- Gerçek zamanlı risk skoru göstergesi (gauge)
- Otomatik tamamlamalı hisse arama
- Detaylı analiz sonuçları ve grafikler
- Responsive tasarım (mobil uyumlu)
- Animasyonlar ve geçiş efektleri

## Teknoloji Stack'i

- **React 18** - UI kütüphanesi
- **TypeScript** - Tip güvenliği
- **Tailwind CSS** - Stil
- **Vite** - Build aracı
- **Recharts** - Grafikler
- **Axios** - API istekleri
- **Lucide React** - İkonlar

## Kurulum

```bash
cd frontend

# Bağımlılıkları yükle
npm install

# Geliştirme sunucusunu başlat
npm run dev
```

## Kullanılabilir Scriptler

- `npm run dev` - Geliştirme sunucusu (http://localhost:3000)
- `npm run build` - Production build
- `npm run preview` - Production build önizleme
- `npm run lint` - ESLint kontrolü

## Proje Yapısı

```
frontend/
├── src/
│   ├── components/       # React komponentleri
│   │   ├── AnalysisResults.tsx
│   │   ├── EventList.tsx
│   │   ├── ExplanationCard.tsx
│   │   ├── Footer.tsx
│   │   ├── Header.tsx
│   │   ├── RiskScoreGauge.tsx
│   │   └── StockSearch.tsx
│   ├── hooks/            # Custom React hooks
│   │   ├── useRiskAnalysis.ts
│   │   └── useStocks.ts
│   ├── services/         # API servisleri
│   │   └── api.ts
│   ├── types/            # TypeScript tipleri
│   │   └── index.ts
│   ├── App.tsx           # Ana uygulama
│   ├── main.tsx          # Entry point
│   └── index.css         # Global stiller
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## Backend Bağlantısı

Frontend, Vite proxy ayarları ile backend'e otomatik bağlanır:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

Backend'in `http://localhost:8000` adresinde çalışıyor olması gerekir.

## Komponentler

### StockSearch
BIST30 hisse senetleri için arama ve seçim komponenti. Otomatik tamamlama özelliği vardır.

### RiskScoreGauge
Risk skorunu gösteren gauge/termometre grafik. Renkli ve animasyonlu.

### AnalysisResults
Analiz sonuçlarını görüntüleyen ana komponent. Skor bileşenleri, olaylar ve açıklamaları içerir.

### EventList
Tespit edilen finansal olayları listeleyen komponent.

### ExplanationCard
Analiz açıklamalarını kartlar halinde gösteren komponent.

## Özelleştirme

### Renkler
Tailwind config'de özelleştirilebilir:

```javascript
// tailwind.config.js
colors: {
  primary: {
    500: '#3b82f6',
    // ...
  },
  risk: {
    low: '#10b981',
    medium: '#f59e0b',
    high: '#ef4444',
    critical: '#7c3aed',
  },
}
```

## Ekran Görüntüleri

Uygulama çalıştığında:
- Ana sayfa: Hisse arama ve popüler hisseler
- Analiz sonuçları: Risk skoru, olaylar, açıklamalar
- Responsive tasarım: Mobil ve masaüstü uyumlu
