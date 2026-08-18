# Crypto Screener

A full-stack cryptocurrency screener built with **FastAPI, React, TypeScript, and the CoinGecko API**.

## Tech Stack

- **Backend:** Python, FastAPI, HTTPX, Pydantic
- **Frontend:** React, TypeScript, Vite
- **API:** CoinGecko

## What I Completed

### Backend

The backend retrieves cryptocurrency data from CoinGecko and filters projects by:

- Market Cap > $0
- FDV < $100M
- 24h Trading Volume > $50K
- Max Supply = Total Supply
- TVL > $50K

The API also supports sorting by:

- Market Capitalization
- 24h Trading Volume

with ascending or descending order.

A health check endpoint is also available:

```text
GET /api/health
```

### Frontend

The frontend:

- Displays cryptocurrency projects in a table
- Supports search by project name
- Supports partial matches, e.g. `eth`
- Supports a custom maximum FDV filter
- Supports sorting by Market Cap
- Supports sorting by 24h Trading Volume
- Supports ascending and descending order (Lowest/Highest first)
- Shows loading and error states
- Communicates only with the backend

## How to Run

### 1. Backend

```
cd backend/apps
```

Create a `.env` file:

```
COINGECKO_API_KEY=your_api_key
COINGECKO_BASE_URL=https://api.coingecko.com/api/v3
CACHE_TTL_SECONDS=300
MAX_DETAIL_CONCURRENCY=8
```

Run the backend:

```
uvicorn app.main:app --reload
```

The backend will be available at:

```
http://localhost:8000
```

### 2. Frontend

Open another terminal:

```
npm install
npm run dev
```

The frontend will be available at:

```
http://localhost:5173
```

## Assumptions and Limitations

**Preview listing:** CoinGecko returned `preview_listing: false` for the available projects. Applying this condition strictly resulted in an empty dataset. Therefore, the value is retrieved and returned by the backend but is not used as a blocking filter.

**Caching:** Results are cached for 5 minutes to reduce unnecessary CoinGecko API requests and avoid rate limits.

**API limits:** The application depends on CoinGecko API availability and rate limits.
