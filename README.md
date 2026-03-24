# FinVis - AI-Powered Financial Risk Analysis System

AI destekli finansal risk analiz sistemi. BIST30 şirketleri için KAP (Kamuyu Aydınlatma Platformu), finansal haber kaynaklarından veri toplar ve NLP tabanlı duygu/olay analizi yaparak risk skorları üretir.

## Özellikler

- **KAP Scraper**: Türkiye'nin resmi Kamuyu Aydınlatma Platformu'ndan açıklamaları çeker
- **News Scraper**: Türkçe finansal haber kaynaklarından veri toplar
- **Duygu Analizi**: HuggingFace Transformers ile Türkçe BERT modelleri kullanır
- **Olay Tespiti**: Finansal risk sinyalleri için kural tabanlı sistem
- **Risk Skorlama**: KAP, haber ve duygu sinyallerini birleştiren ağırlıklı algoritma
- **RESTful API**: FastAPI tabanlı uç noktalar
- **Modern Arayüz**: React + TypeScript + Tailwind CSS dashboard
- **Caching**: Performans için bellek içi önbellekleme
- **Logging**: Kapsamlı loglama

## Teknoloji Stack'i

### Backend
- **Python 3.9+**, FastAPI
- **HuggingFace Transformers**, Turkish BERT
- **requests**, BeautifulSoup (scraping)
- **Pydantic** (veri doğrulama)
- **loguru** (logging)

### Frontend
- **React 18**, TypeScript
- **Tailwind CSS** (stil)
- **Vite** (build aracı)
- **Recharts** (grafikler)
- **Axios** (API istekleri)

## Proje Yapısı

```
finvis/
├── backend/              # Python FastAPI backend
│   ├── app.py
│   ├── requirements.txt
│   ├── routes/
│   ├── scrapers/
│   ├── nlp/
│   ├── scoring/
│   ├── models/
│   └── utils/
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Hızlı Başlangıç

### 1. Backend'i Başlat

```bash
cd backend

# Sanal ortam oluştur (önerilir)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Sunucuyu çalıştır
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Backend şu adreslerde çalışacak:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 2. Frontend'i Başlat

Yeni bir terminal aç:

```bash
cd frontend

# Bağımlılıkları yükle
npm install

# Geliştirme sunucusunu başlat
npm run dev
```

Frontend şu adreste çalışacak:
- UI: http://localhost:3000

## Kullanım

### Web Arayüzü

Tarayıcıda `http://localhost:3000` adresine gidin:
1. Hisse senedi arama kutusuna sembol girin (örn: THYAO, GARAN)
2. "Analiz Et" butonuna tıklayın veya listeden seçin
3. Risk skoru, olaylar ve detaylı analizi görüntüleyin

### API Kullanımı

```bash
# Risk analizi için
curl http://localhost:8000/api/v1/risk/THYAO

# Mevcut hisseleri listele
curl http://localhost:8000/api/v1/stocks

# Toplu analiz
curl "http://localhost:8000/api/v1/risk/batch?symbols=THYAO&symbols=GARAN"
```

## API Örnek Yanıt

```json
{
  "stock": "THYAO",
  "risk_score": 42,
  "risk_level": "low",
  "sentiment": "positive",
  "sentiment_confidence": 0.75,
  "events": [
    {
      "event_type": "positive",
      "keyword": "yatırım",
      "context": "Şirketimiz yeni yatırım planlarını açıkladı...",
      "risk_impact": 4
    }
  ],
  "explanations": [
    "✅ Düşük risk seviyesi (42/100).",
    "Skor bileşenleri: KAP açıklamaları (38.0 x 0.5)...",
    "Analiz edilen kaynaklar: 3 KAP açıklaması, 3 haber makalesi..."
  ],
  "breakdown": {
    "kap_score": 38.0,
    "news_score": 45.0,
    "sentiment_score": 35.0,
    "kap_contribution": 19.0,
    "news_contribution": 13.5,
    "sentiment_contribution": 7.0
  },
  "data_sources": {
    "kap_disclosures": 3,
    "news_articles": 3,
    "detected_events": 4,
    "sentiment_analyses": 6
  },
  "analyzed_at": "2024-01-15T10:30:00"
}
```

## Risk Skorlama Algoritması

```
risk_skoru = 0.5 × kap_skoru + 0.3 × haber_skoru + 0.2 × duygu_skoru
```

**Risk Seviyeleri:**
- 0-30: Çok Düşük Risk ✅
- 30-50: Düşük Risk ✓
- 50-70: Orta Risk ⚡
- 70-100: Yüksek/Kritik Risk ⚠️

**Veri Kaynakları:**
- **KAP (50%)**: Resmi Kamuyu Aydınlatma Platformu açıklamaları
- **Haberler (30%)**: Finansal haber analizi
- **Duygu (20%)**: Metin duygu analizi

## Olay Tespiti

Sistem Türkçe finansal anahtar kelimeler kullanır:

**Yüksek Risk:**
- zarar, kayıp, ceza, soruşturma, iflas, dava

**Pozitif:**
- kâr, yatırım, büyüme, anlaşma, ihracat

## Ekran Görüntüleri

### Ana Sayfa
- Modern hisse arama arayüzü
- Popüler hisseler için hızlı seçim
- Özellik kartları

### Analiz Sonuçları
- Renkli risk skoru göstergesi (gauge)
- Skor bileşenleri (KAP, Haber, Duygu)
- Tespit edilen olaylar listesi
- Detaylı açıklamalar

## Konfigürasyon

`.env` dosyası ile yapılandırılabilir:

```env
# API Ayarları
API_DEBUG=True
PORT=8000

# NLP Model
SENTIMENT_MODEL=savasy/bert-base-turkish-cased-sentiment

# Risk Ağırlıkları
KAP_WEIGHT=0.5
NEWS_WEIGHT=0.3
SENTIMENT_WEIGHT=0.2

# Cache
CACHE_TTL_SECONDS=300
```

## Git ve GitHub

Uzak repo: [kaplancanali/finwizardai](https://github.com/kaplancanali/finwizardai)

Değişiklikleri kaydetmek ve GitHub’a göndermek:

```bash
git status                    # ne değişti
git add -A                    # tümünü sahneye al
git commit -m "Kısa açıklama" # yerel commit
git push                      # origin/main’e gönder
```

`nothing to commit, working tree clean` görürsen: commit edilecek yeni değişiklik yok demektir; önce dosyalarda düzenleme yap.

### Vercel (finwizardai.vercel.app 404)

Kök dizinde yalnızca `frontend/` Vite projesi olduğu için Vercel’de **Root Directory** boş bırakılırsa build üretilmez ve **404 NOT_FOUND** görülür. Repoda kök `vercel.json` bu yolu ayarlar; yine de Vercel’de **Redeploy** yapın.

Canlı sitede API çağrıları için backend’i ayrı yayınlayın (Railway, Render, Fly vb.); Vercel statik frontend `/api` sunmaz.

**API adresini verme (ikisinden biri):**

1. `frontend/public/api-config.json` içinde `"apiBase": "https://senin-backend.com/api/v1"` (sonda `/` yok) yazıp commit + deploy — `VITE_API_URL` şart değil.
2. Veya host panelinde `VITE_API_URL` ile aynı tabanı build ortamına verip yeniden derleyin.

## Geliştirme

### Backend Testleri
```bash
cd backend
pytest
```

### Frontend Lint
```bash
cd frontend
npm run lint
```

### Production Build
```bash
# Backend
uvicorn app:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
npm run preview
```

## Gelecek Geliştirmeler

- [x] Modern web arayüzü ✅
- [ ] Twitter/X entegrasyonu
- [ ] PostgreSQL veritabanı
- [ ] Gerçek zamanlı veri akışı
- [ ] Tarihsel trend analizi
- [ ] Risk eşik uyarı sistemi
- [ ] ML tabanlı olay sınıflandırma

## Lisans

MIT License

## Sorumluluk Reddi

Bu sistem sadece bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir. Yatırım kararları öncesinde nitelikli finansal danışmanlara başvurunuz.

---

**FinVis** - AI Destekli Finansal Risk Analizi
