import os
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from catalog import Catalog
from agent import Agent
from models import ChatRequest, ChatResponse

_catalog: Catalog | None = None
_agent: Agent | None = None

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _catalog, _agent
    dataset_path = os.environ.get("DATASET_PATH", "dataset.json")
    _catalog = Catalog(dataset_path)
    _agent = Agent(_catalog)
    yield


app = FastAPI(title="SHL Assessment Recommender", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not _agent:
        raise HTTPException(status_code=503, detail="Service not ready")
    if not request.messages:
        raise HTTPException(status_code=422, detail="messages list is empty")
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    try:
        return _agent.chat(messages)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"LLM error: {exc}") from exc


# Serve built React frontend (after npm run build)
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str = ""):
        index = STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(index)
        raise HTTPException(status_code=404, detail="Frontend not built yet")
