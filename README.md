# TrendScope

A high-performance real-time economic sentiment monitor that tracks market mood across 7 global regions using state-of-the-art sentiment analysis.

## What it does

TrendScope monitors economic news from Google News RSS feeds every 15 minutes, analyzes headlines using a quantized FinancialBERT model, and generates a live "bull vs bear" optimism index. It provides a crystal-clear view of economic momentum across major global markets, filtering out the noise to focus on high-impact signals.

## Regions tracked

- **Global** - Worldwide market trends
- **United States** - Wall Street and Fed sentiment
- **European Union** - Eurozone economic signals
- **Africa** - Emerging market development
- **Egypt** - Local economic indicators
- **Saudi Arabia** - Vision 2030 and energy markets
- **Middle East** - Regional trade and commerce

## Key Features

- **High-Resolution Tracking**: Data collected every 15 minutes for real-time reactivity.
- **Micro-Quantized AI**: Powered by a distilled FinancialBERT (ONNX Int8) for professional-grade sentiment analysis.
- **Memory Optimized**: Highly efficient "DB-first" architecture saving ~1GB of RAM vs standard ML deployments.
- **Premium UI**: Modern, high-performance dashboard with horizontal scrolling trends and sticky reference axes.
- **Mobile First**: Fully responsive layout designed for professional monitoring on any device.
- **Dual Language**: Formal English and Arabic support (RTL).

## Tech stack

**Backend:** FastAPI + Celery + Redis + SQLite  
**Sentiment Engine:** Distilled FinancialBERT (ONNX Runtime)  
**Frontend:** SvelteKit + Vanilla CSS (Custom Design System)  
**Infrastructure:** Dockerized for streamlined VPS deployment

## Getting Started

### 1. Build the AI Model

To prepare the model for production (quantization):

```bash
cd backend
python build_model.py
```

### 2. Run with Docker (Recommended)

```bash
docker-compose up --build
```

The dashboard will be available at `http://localhost:3000`

## Production Health Checks (Coolify)

Use dedicated liveness endpoints to avoid false negatives and silent timeouts:

- Frontend liveness: `/healthz` or `/health` on port `3000`
- Backend liveness: `/health/live`, `/healthz`, or `/health` on port `8000`
- Backend readiness diagnostics: `/health/ready` or `/api/health`

Recommended behavior for reverse proxies/orchestrators:

- Mark service healthy from liveness endpoints only.
- Keep startup grace periods >= 45s for frontend and >= 60s for backend.
- Do not gate frontend or backend startup on dependency health; let the app start and expose degraded status in readiness diagnostics instead.

Quick manual verification after deploy:

```bash
curl -i http://localhost:3000/healthz
curl -i http://localhost:8000/health/live
curl -i http://localhost:8000/health
```

### 3. Manual Development

**Backend:**

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## How sentiment analysis works

TrendScope uses a sophisticated two-stage pipeline:

1.  **Signal Isolation**: Headlines are passed through a noise filter that removes fluff (podcasts, guides, newsletters) to focus purely on economic events.
2.  **AI Classification**: The remaining headlines are analyzed by a **FinancialBERT** model specifically trained on market data. Unlike basic keyword scrapers, it understands financial context (e.g., "interest rates hold steady" vs "holdings liquidated").

The final score is calculated using the **Optimism Ratio**:

```
Sentiment Score = Bullish Signals / (Bullish + Bearish Signals) × 100
```

Scores above 50% indicate an optimistic outlook, while scores below 50% signal bearish sentiment.

## License

MIT - Created by [Mohammed Essam](https://mohammedeabdelaziz.github.io/)
