# main.py
import os
import asyncio
from typing import List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import AsyncOpenAI

# ------------------------------------------------------------------
#  FastAPI init
# ------------------------------------------------------------------
app = FastAPI(title="Apple AI Orchestrator 2.0")

# Mount static files (your CSS/JS/HTML)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ------------------------------------------------------------------
#  Serve the front-end page
# ------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# ------------------------------------------------------------------
#  OpenAI client (>=1.0) – key from env
# ------------------------------------------------------------------
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------------------------------------------
#  Stub agents (replace with real logic)
# ------------------------------------------------------------------
async def file_agent(query: str, files: List[UploadFile]) -> Dict[str, Any]:
    await asyncio.sleep(0.5)
    return {"summary": f"Processed {len(files)} file(s) for: {query[:40]}…"}

async def research_agent(query: str) -> Dict[str, Any]:
    await asyncio.sleep(0.6)
    return {"summary": f"Research completed for '{query[:40]}…'"}

async def analysis_agent(query: str) -> Dict[str, Any]:
    await asyncio.sleep(0.7)
    return {"summary": "Strategic insights generated."}

async def mail_agent(query: str) -> Dict[str, Any]:
    await asyncio.sleep(0.4)
    return {"summary": "Professional email drafted & ready."}

async def calendar_agent(query: str) -> Dict[str, Any]:
    await asyncio.sleep(0.5)
    return {"summary": "Calendar updated with new event(s)."}

AGENT_MAP = {
    "file_agent": file_agent,
    "research_agent": research_agent,
    "analysis_agent": analysis_agent,
    "mail_agent": mail_agent,
    "calendar_agent": calendar_agent,
}

# ------------------------------------------------------------------
#  Single orchestration endpoint
# ------------------------------------------------------------------
@app.post("/execute")
async def execute(
    query: str = Form(...),
    files: List[UploadFile] = File([])
):
    start = datetime.utcnow()
    executed: List[str] = []
    agent_results: List[Dict[str, Any]] = []

    # Decide which agents to run (very naïve)
    to_run = []
    if files:
        to_run.append("file_agent")
    if "meeting" in query.lower() or "schedule" in query.lower():
        to_run.extend(["calendar_agent", "mail_agent"])
    if "research" in query.lower() or "market" in query.lower():
        to_run.append("research_agent")
    if not to_run:     # fallback
        to_run = ["analysis_agent"]

    # Run them concurrently
    coros = []
    for name in to_run:
        if name == "file_agent":
            coros.append(AGENT_MAP[name](query, files))
        else:
            coros.append(AGENT_MAP[name](query))
    results = await asyncio.gather(*coros)

    # Build response
    for name, result in zip(to_run, results):
        executed.append(name)
        agent_results.append({
            "agent": name,
            "status": "success",
            **result,
            "results": {"details": f"Detailed output from {name}"}
        })

    return {
        "success": True,
        "data": {
            "query": query,
            "agents_executed": executed,
            "status": "completed",
            "summary": "Multi-agent orchestration finished successfully.",
            "agent_results": agent_results,
            "orchestration_metadata": {
                "duration_sec": (datetime.utcnow() - start).total_seconds(),
                "total_agents": len(executed),
                "files_processed": len(files)
            }
        }
    }

# ------------------------------------------------------------------
#  Run:  uvicorn main:app --reload
# ------------------------------------------------------------------
