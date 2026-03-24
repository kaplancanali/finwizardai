# FinVis - AI-Powered Financial Risk Analysis System

An AI-powered financial risk analysis system for BIST30 (Borsa Istanbul 30) companies. The system collects data from KAP (Public Disclosure Platform), financial news sources, and performs NLP-based sentiment and event analysis to output risk scores.

## Features

- **KAP Scraper**: Fetches official disclosures from Turkey's Public Disclosure Platform
- **News Scraper**: Collects financial news from multiple Turkish sources
- **Sentiment Analysis**: Uses HuggingFace Transformers with Turkish BERT models
- **Event Detection**: Rule-based system for financial risk signal detection
- **Risk Scoring Engine**: Weighted algorithm combining KAP, news, and sentiment signals
- **RESTful API**: FastAPI-based endpoints for easy integration
- **Caching**: In-memory caching for improved performance
- **Logging**: Comprehensive logging with loguru

## Tech Stack

- **Backend**: Python, FastAPI
- **AI/NLP**: HuggingFace Transformers, Turkish BERT models
- **Scraping**: requests, BeautifulSoup
- **Data Validation**: Pydantic
- **Logging**: loguru
- **Testing**: pytest

## Project Structure

```
backend/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── routes/               # API routes
│   ├── __init__.py
│   └── risk.py          # Risk analysis endpoints
├── scrapers/            # Data collection modules
│   ├── __init__.py
│   ├── kap_scraper.py   # KAP (Public Disclosure) scraper
│   └── news_scraper.py  # Financial news scraper
├── nlp/                 # NLP modules
│   ├── __init__.py
│   ├── sentiment.py     # Sentiment analysis
│   └── event_detector.py # Event detection
├── scoring/             # Risk scoring
│   ├── __init__.py
│   └── risk_engine.py   # Main risk scoring engine
├── models/              # Data models
│   ├── __init__.py
│   └── schemas.py       # Pydantic models
├── utils/               # Utilities
│   ├── __init__.py
│   ├── config.py        # Configuration management
│   ├── cache.py         # Caching utilities
│   └── logger.py        # Logging setup
├── services/            # Business logic (future)
│   └── __init__.py
└── logs/                # Log files (created at runtime)
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env with your preferences
```

### 3. Run the Server

```bash
# Development mode with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app:app --host 0.0.0.0 --port 8000
```

### 4. Access the API

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## API Endpoints

### Get Risk Analysis

```bash
GET /api/v1/risk/{stock_symbol}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/risk/THYAO
```

**Response:**
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

### Batch Analysis

```bash
GET /api/v1/risk/batch?symbols=THYAO&symbols=GARAN&symbols=ASELS
```

### List Available Stocks

```bash
GET /api/v1/stocks
```

### Health Check

```bash
GET /api/v1/health
```

### Clear Cache

```bash
POST /api/v1/cache/clear
```

## Risk Scoring Algorithm

The risk score is calculated using a weighted combination:

```
risk_score = 0.5 × kap_score + 0.3 × news_score + 0.2 × sentiment_score
```

**Risk Levels:**
- 0-30: Very Low Risk
- 30-50: Low Risk
- 50-70: Medium Risk
- 70-100: High Risk

**Data Sources:**
- **KAP (50%)**: Official disclosures from Turkey's Public Disclosure Platform
- **News (30%)**: Financial news sentiment and event detection
- **Sentiment (20%)**: Overall text sentiment analysis

## Event Detection

The system detects financial events using keyword patterns:

**High Risk Events:**
- zarar, kayıp (financial loss)
- ceza, para cezası (penalty)
- soruşturma, inceleme (investigation)
- iflas, konkordato (bankruptcy)
- dava, mahkeme (lawsuit)

**Positive Events:**
- kâr, kazanç (profit)
- yatırım, proje (investment)
- büyüme, artış (growth)
- anlaşma, sözleşme (contract)
- ihracat (export)

## Supported Stocks

The system supports all BIST30 stocks including:
- THYAO (Türk Hava Yolları)
- GARAN (Garanti Bankası)
- ASELS (Aselsan)
- ISCTR (İş Bankası)
- KCHOL (Koç Holding)
- And 25+ more...

See `/api/v1/stocks` for the complete list.

## Configuration

Configuration is managed through environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `API_DEBUG` | Debug mode | `True` |
| `PORT` | Server port | `8000` |
| `SENTIMENT_MODEL` | HuggingFace model | `savasy/bert-base-turkish-cased-sentiment` |
| `KAP_WEIGHT` | KAP score weight | `0.5` |
| `NEWS_WEIGHT` | News score weight | `0.3` |
| `SENTIMENT_WEIGHT` | Sentiment weight | `0.2` |
| `CACHE_TTL_SECONDS` | Cache duration | `300` |

## Development

### Running Tests

```bash
pytest
```

### Adding New Features

1. Scrapers: Add new scraper classes in `scrapers/`
2. NLP: Extend sentiment or event detection in `nlp/`
3. Scoring: Modify risk calculation in `scoring/risk_engine.py`
4. API: Add new endpoints in `routes/`

## Future Enhancements

- [ ] Twitter/X integration
- [ ] PostgreSQL database persistence
- [ ] Real-time data streaming
- [ ] Historical trend analysis
- [ ] Web dashboard UI
- [ ] Alert system for risk threshold breaches
- [ ] ML-based event classification

## License

MIT License

## Disclaimer

This system is for informational purposes only. It does not constitute investment advice. Always consult with qualified financial advisors before making investment decisions.
