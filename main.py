# main.py
import asyncio
import json
from typing import List

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
import os

app = FastAPI(title="Apple AI Orchestrator 2.0")

# Mount the static folder that contains style.css and script.js
app.mount("/static", StaticFiles(directory="static"), name="static")

# ------------------------------------------------------------------
# 1. Serve the HTML you posted
# ------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# ------------------------------------------------------------------
# 2. Request/response models
# ------------------------------------------------------------------
class OrchestrateRequest(BaseModel):
    query: str
    files: List[str] = []   # we’ll ignore content for the PoC

class AgentProgress(BaseModel):
    agent: str
    status: str

# ------------------------------------------------------------------
# 3. OpenAI client (>=1.0)
# ------------------------------------------------------------------
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------------------------------------------
# 4. Stub agents
# ------------------------------------------------------------------
async def file_agent(query: str) -> str:
    await asyncio.sleep(1)
    return "📄 File processing complete."

async def research_agent(query: str) -> str:
    await asyncio.sleep(1)
    return "🔍 Research summary generated."

async def analysis_agent(query: str) -> str:
    await asyncio.sleep(1)
    return "🧠 Strategic insights ready."

async def mail_agent(query: str) -> str:
    await asyncio.sleep(1)
    return "📧 Draft email prepared."

async def calendar_agent(query: str) -> str:
    await asyncio.sleep(1)
    return "📅 Calendar updated."

AGENTS = [
    ("file_agent", file_agent),
    ("research_agent", research_agent),
    ("analysis_agent", analysis_agent),
    ("mail_agent", mail_agent),
    ("calendar_agent", calendar_agent),
]

# ------------------------------------------------------------------
# 5. Orchestration endpoint
#    Example curl:
#    curl -X POST http://localhost:8000/execute-orchestration \
#         -F "query=Schedule meeting about Q4 planning"
# ------------------------------------------------------------------
@app.post("/execute-orchestration")
async def execute_orchestration(
    query: str = Form(...),
    files: List[UploadFile] = File([])
):
    results = {}

    # Stream progress back (server-sent events style)
    async def generate():
        for agent_name, coro in AGENTS:
            yield f"data: {json.dumps({'agent': agent_name, 'status': 'running'})}\n\n"
            try:
                results[agent_name] = await coro(query)
                yield f"data: {json.dumps({'agent': agent_name, 'status': 'done', 'result': results[agent_name]})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'agent': agent_name, 'status': 'error', 'error': str(e)})}\n\n"
        # final payload
        yield f"data: {json.dumps({'type': 'final', 'results': results})}\n\n"

    from fastapi.responses import StreamingResponse
    return StreamingResponse(generate(), media_type="text/plain")

# ------------------------------------------------------------------
# 6. Run:  uvicorn main:app --reload
# ------------------------------------------------------------------
