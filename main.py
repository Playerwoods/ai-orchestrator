# main.py  (copy-paste entire file)
import os, asyncio, json, textwrap
from datetime import datetime
from typing import List, Dict, Any

from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from openai import AsyncOpenAI

# -------------------------------------------------
# FastAPI init
# -------------------------------------------------
app = FastAPI(title="Apple AI Orchestrator 2.0")

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------------------------
# Stub agents (replace with real logic later)
# -------------------------------------------------
async def file_agent(query: str, files: List[UploadFile]) -> Dict[str, Any]:
    await asyncio.sleep(0.5)
    return {"summary": f"Processed {len(files)} file(s) for: {query[:60]}…"}

async def research_agent(query: str) -> Dict[str, Any]:
    await asyncio.sleep(0.6)
    return {"summary": f"Research summary for '{query[:60]}…'"}

async def analysis_agent(query: str) -> Dict[str, Any]:
    await asyncio.sleep(0.7)
    return {"summary": "Strategic insights generated"}

async def mail_agent(query: str) -> Dict[str, Any]:
    await asyncio.sleep(0.4)
    return {"summary": "Email drafted & queued"}

async def calendar_agent(query: str) -> Dict[str, Any]:
    await asyncio.sleep(0.5)
    return {"summary": "Calendar updated"}

AGENTS = {
    "file_agent": file_agent,
    "research_agent": research_agent,
    "analysis_agent": analysis_agent,
    "mail_agent": mail_agent,
    "calendar_agent": calendar_agent,
}

# -------------------------------------------------
# Single endpoint
# -------------------------------------------------
@app.post("/execute")
async def execute(
    query: str = Form(...),
    files: List[UploadFile] = File([])
):
    start = datetime.utcnow()
    to_run = ["analysis_agent"]
    if files:
        to_run.insert(0, "file_agent")
    if any(k in query.lower() for k in ("meeting", "schedule", "calendar")):
        to_run.extend(["calendar_agent", "mail_agent"])
    if any(k in query.lower() for k in ("research", "market", "competitive")):
        to_run.append("research_agent")

    coros = [
        AGENTS[name](query, files) if name == "file_agent" else AGENTS[name](query)
        for name in to_run
    ]
    results = await asyncio.gather(*coros)

    agent_results = [
        {
            "agent": name,
            "status": "success",
            "summary": res["summary"],
            "results": {"details": f"Detailed output from {name}"}
        }
        for name, res in zip(to_run, results)
    ]

    return {
        "success": True,
        "data": {
            "query": query,
            "agents_executed": to_run,
            "status": "completed",
            "summary": "Multi-agent orchestration finished successfully",
            "agent_results": agent_results,
            "orchestration_metadata": {
                "duration_sec": (datetime.utcnow() - start).total_seconds(),
                "total_agents": len(to_run),
                "files_processed": len(files)
            }
        }
    }

# -------------------------------------------------
# Serve the front-end HTML (embedded)
# -------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=FRONTEND_HTML)

# -------------------------------------------------
# The exact HTML/CSS/JS you posted, minified into one string
# -------------------------------------------------
FRONTEND_HTML = textwrap.dedent("""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Apple AI Orchestrator 2.0</title>
<style>
*{box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif}
body{margin:0;background:#0f0f0f;color:#e5e5e5;line-height:1.6}
.container{max-width:1000px;margin:0 auto;padding:2rem}
header{text-align:center;margin-bottom:2rem}
h1{font-size:2.2rem;margin:.2rem 0}
.subtitle{font-size:1rem;color:#aaa}
.stats-grid{display:flex;justify-content:space-around;margin-bottom:2rem}
.stat-card{background:#1c1c1e;border-radius:12px;padding:1.5rem;text-align:center;flex:1 1 0;margin:.5rem}
.stat-number{font-size:2rem;font-weight:700}
.orchestrator-panel{background:#1c1c1e;border-radius:12px;padding:1.5rem;margin-bottom:2rem}
textarea{width:100%;border:none;border-radius:8px;padding:.75rem;background:#2c2c2e;color:#fff;resize:vertical}
button{cursor:pointer;background:#007aff;color:#fff;border:none;padding:.75rem 1.5rem;border-radius:8px;font-size:1rem;margin-top:.5rem}
button:disabled{opacity:.5;cursor:not-allowed}
.example-btn{background:#333;border:1px solid #444;border-radius:8px;padding:.5rem;margin:.25rem;font-size:.85rem}
.examples-grid{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:.5rem}
.agent-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:1rem;margin-top:1rem}
.agent-card{background:#2c2c2e;border-radius:8px;padding:1rem;text-align:center}
.agent-icon{font-size:2rem}
.result-section{background:#1c1c1e;border-left:4px solid #007aff;padding:1rem;margin:.5rem 0;border-radius:8px}
.hidden{display:none}
.agent-step{border-left:4px solid #007aff;padding:.5rem;margin:.25rem 0;border-radius:4px}
</style>
</head>
<body>
<div class="container">
 <header>
  <h1>🤖 Apple AI Orchestrator 2.0</h1>
  <p>Multi-agent intelligence for document processing and analysis</p>
 </header>

 <main>
  
