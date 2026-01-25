# TrendScope

A real-time economic sentiment monitor that tracks news sentiment across 7 global regions.

## What it does

TrendScope scrapes economic news from Google News RSS feeds every hour, runs sentiment analysis on the headlines, and displays an aggregated "optimism vs pessimism" score for each region. You can see at a glance whether the news coming out of Egypt, Saudi Arabia, the EU, or other regions is leaning positive or negative.

## Regions tracked

- Global
- United States
- European Union
- Africa
- Egypt
- Saudi Arabia
- Middle East

## Tech stack

**Backend:** FastAPI + Python + TextBlob for sentiment analysis  
**Frontend:** SvelteKit + Tailwind CSS  
**Scheduling:** Celery + Redis for hourly data collection  
**Database:** SQLite for storing historical data

## Running locally

### Development (without Docker)

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

### Production (with Docker)

```bash
docker-compose up --build
```

The app will be available at `http://localhost:3000`

## API endpoints

| Endpoint                         | Description                        |
| -------------------------------- | ---------------------------------- |
| `GET /api/regions`               | All regions with current sentiment |
| `GET /api/regions/{id}`          | Single region data                 |
| `GET /api/regions/{id}/trend`    | 24h sentiment trend                |
| `GET /api/regions/{id}/insights` | Auto-generated insights            |
| `GET /health`                    | Health check                       |
| `POST /api/collect`              | Trigger manual data collection     |

## How sentiment works

Each headline gets analyzed with TextBlob and boosted/penalized based on economic keywords:

- **Positive:** growth, investment, profit, expansion, etc.
- **Negative:** recession, crisis, layoffs, inflation, etc.

Headlines are then categorized as optimistic (>0.2), pessimistic (<-0.2), or neutral. The final score is calculated as:

```
Score = Optimistic / (Optimistic + Pessimistic) × 100
```

Neutral headlines don't affect the score — this filters out the noise.

## Arabic support

The UI supports both English and Arabic. Click the language button in the header to switch. The Arabic version uses IBM Plex Sans Arabic for better readability.

## License

MIT
