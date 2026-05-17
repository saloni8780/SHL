# SHL Assessment Recommender

A conversational AI assistant that helps hiring managers and recruiters select the right SHL talent assessments for any role. Describe who you're hiring and the system recommends a balanced battery of up to 10 assessments from a catalog of 377 tests.

## Features

- Multi-turn chat interface — clarifies vague requests before recommending
- BM25 retrieval with anchor injection to surface the most relevant assessments
- Structured JSON responses from Gemini 2.5-Flash-Lite (no hallucinated URLs)
- Assessment cards with type badges and direct links to the SHL catalog
- Conversation auto-closes after confirmation or 8 turns

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| LLM | Google Gemini 2.5-Flash-Lite (`google-genai`) |
| Retrieval | BM25 (`rank-bm25`) |
| Frontend | React 19 + Vite |
| Deployment | Render (web service + static site) |

## Project Structure

```
SHL/
├── main.py              # FastAPI app, /chat endpoint, static file serving
├── agent.py             # LLM integration, system prompt, response schema
├── catalog.py           # Dataset loading, BM25 retrieval pipeline
├── models.py            # Pydantic request/response models
├── dataset.json         # 377 SHL assessments
├── requirements.txt
├── Dockerfile
├── render.yaml          # Render Blueprint (backend + frontend services)
└── frontend/
    ├── src/
    │   ├── App.jsx              # Chat UI, message history, API calls
    │   └── components/
    │       ├── RecommendationCard.jsx
    │       └── TypingIndicator.jsx
    └── package.json
```

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Google AI Studio](https://aistudio.google.com) API key (free)

### Backend

```bash
# Clone the repo
git clone https://github.com/saloni8780/SHL.git
cd SHL

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
echo "GOOGLEAI_API_KEY=your_key_here" > .env

# Run the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### Frontend (development)

```bash
cd frontend
npm install
npm run dev
```

The dev server runs at `http://localhost:5173` and proxies `/chat` to the backend.

### Frontend (served by backend)

```bash
cd frontend
npm run build
cp -r dist ../static    # Windows: xcopy dist ..\static /E /I
```

Then visit `http://localhost:8000` — the FastAPI server serves the built React app directly.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOOGLEAI_API_KEY` | Yes | Google AI Studio API key |
| `LLM_MODEL` | No | Model name (default: `gemini-2.5-flash-lite`) |
| `DATASET_PATH` | No | Path to assessment catalog (default: `dataset.json`) |
| `VITE_API_URL` | Frontend only | Backend base URL when deployed separately |

## API

### `POST /chat`

```json
{
  "messages": [
    { "role": "user", "content": "I need to hire a senior Java developer" }
  ]
}
```

**Response:**

```json
{
  "reply": "Here are assessments suited for a senior Java developer role.",
  "recommendations": [
    {
      "name": "SHL Verify Interactive G+",
      "url": "https://www.shl.com/...",
      "test_type": "A"
    }
  ],
  "end_of_conversation": false
}
```

Test type codes: `A` Ability · `B` Biodata · `C` Competencies · `D` Development · `E` Exercises · `K` Knowledge · `P` Personality · `S` Simulations

### `GET /health`

Returns `{"status": "ok"}` — used by Render for health checks.

## How It Works

1. **Retrieval** — User messages are used to query the catalog via BM25. The top 15 results are combined with 2 fixed anchor assessments (OPQ32r for personality, Verify G+ for cognitive) and a supplementary cognitive query, deduplicated to 20 candidates.

2. **Prompt** — The system prompt encodes four actions: `CLARIFY` (ask one question if the query is vague), `RECOMMEND` (return a balanced battery), `REFINE` (update on new constraints), and `CONFIRM & CLOSE` (end the conversation). Off-topic requests are refused.

3. **Validation** — All URLs in the LLM response are checked against the catalog URL set. Invalid URLs are stripped before the response is returned.

## Docker

```bash
docker build -t shl-recommender .
docker run -p 8000:8000 -e GOOGLEAI_API_KEY=your_key_here shl-recommender
```

## Deploy on Render

The `render.yaml` defines two services:

- **`shl-recommender`** — Python web service (Docker), hosts the FastAPI backend
- **`shl-frontend`** — Static site, builds and serves the React app

**Steps:**

1. Push the repo to GitHub
2. Go to Render → **New → Blueprint** 
3. Set `GOOGLEAI_API_KEY` when prompted
4. Set `VITE_API_URL` on the frontend service to your backend's Render URL (e.g., `https://shl-recommender.onrender.com`)
5. Click **Deploy Blueprint**

## License

MIT
