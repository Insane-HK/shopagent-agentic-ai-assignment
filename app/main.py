import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from agent.agent import run_agent_with_trace
import os

app = FastAPI(title="ShopAgent API", version="1.0.0", docs_url="/api/docs")

# serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class ChatMessage(BaseModel):
    role: str
    text: str

class ChatRequest(BaseModel):
    question: str
    history: list[ChatMessage] = Field(default_factory=list)


class ToolCall(BaseModel):
    tool: str
    input: dict
    output: dict


class ChatResponse(BaseModel):
    answer: str
    trace: list
    duration_ms: int


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    t0 = time.time()
    try:
        # convert pydantic models to dicts
        history_dicts = [{"role": msg.role, "text": msg.text} for msg in req.history]
        res = run_agent_with_trace(req.question.strip(), history=history_dicts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    elapsed = int((time.time() - t0) * 1000)
    return ChatResponse(
        answer=res["answer"],
        trace=res.get("trace", []),
        duration_ms=elapsed,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
