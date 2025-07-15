# main.py  —  entire file, drop-in replacement
import os
import asyncio
import json
import httpx
from datetime import datetime
from typing import List, Dict, Any

from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from openai import AsyncOpenAI

# -------------------------------------------------
# FastAPI app
# -------------------------------------------------
app = FastAPI(title="Apple AI Orchestrator 2.0")

# -------------------------------------------------
# Environment keys
# -------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")  # <- your Serper key is read here

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# -------------------------------------------------
# Real Research-Agent using Serper
# -------------------------------------------------
async def research_agent(query: str) -> Dict[str, Any]:
    if not SERPER_API_KEY:
        return {"summary": "No SERPER_API_KEY configured."}

    payload = {"q": query, "num": 5}
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}

    async with httpx.AsyncClient() as http:
        r = await http.post("https://google.serper.dev/search", json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()

    organic = data.get("organic", [])
    summary = "\n".join([f"{i+1}. {o['title']} ({o['link']})" for i, o in enumerate(organic[:3])])
    return {"summary": summary or "No results found."}

# -------------------------------------------------
# Stub agents
# -------------------------------------------------
async def file_agent(query: str, files: List[UploadFile]) -> Dict[str, Any]:
    await asyncio.sleep(0.5)
    return {"summary": f"Processed {len(files)} file(s)."}

async def analysis_agent(query: str) -> Dict[str, Any]:
    await asyncio.sleep(0.7)
    return {"summary": "Strategic insights generated"}

async def mail_agent(query: str) -> Dict[str, Any]:
    await asyncio.sleep(0.4)
    return {"summary": "Email drafted"}

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
# /execute endpoint
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
# Serve front-end
# -------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=INDEX_HTML)

INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1">
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
  <div class="stats-grid">
   <div class="stat-card"><div class="stat-number">5</div><div class="stat-label">AI Agents</div></div>
   <div class="stat-card"><div class="stat-number">∞</div><div class="stat-label">Workflows</div></div>
   <div class="stat-card"><div class="stat-number">🔒</div><div class="stat-label">Privacy First</div></div>
  </div>

  <div class="orchestrator-panel">
   <h2>🎯 Multi-Agent Orchestration</h2>
   <textarea id="queryInput" placeholder="Tell the AI what you need..." rows="3"></textarea>
   <input type="file" id="fileInput" multiple style="display:none"/>
   <label for="fileInput" style="cursor:pointer;color:#007aff;text-decoration:underline">📎 Upload Documents</label><br/>
   <button onclick="executeOrchestration()" id="executeBtn">🚀 Execute Orchestration</button>

   <h3>💡 Example Orchestrations</h3>
   <div class="examples-grid">
    <button class="example-btn" onclick="setExample('Schedule a meeting about AI automation strategy')">📅 Schedule Meeting</button>
    <button class="example-btn" onclick="setExample('Extract action items from uploaded documents')">📧 Extract Action Items</button>
    <button class="example-btn" onclick="setExample('Block deep-work time for quarterly planning')">⏰ Time Blocking</button>
    <button class="example-btn" onclick="setExample('Research AI automation market')">🔍 Market Research</button>
    <button class="example-btn" onclick="setExample('Prepare for tomorrow board meeting')">🎯 Meeting Prep</button>
    <button class="example-btn" onclick="setExample('Analyze uploaded PDFs and extract insights')">📊 Document Analysis</button>
   </div>

   <h3>🤖 Available Agents</h3>
   <div class="agent-cards">
    <div class="agent-card"><div class="agent-icon">📄</div><div class="agent-name">File Agent</div><div class="agent-desc">PDF processing, text extraction</div></div>
    <div class="agent-card"><div class="agent-icon">🔍</div><div class="agent-name">Research Agent</div><div class="agent-desc">Web search, market analysis</div></div>
    <div class="agent-card"><div class="agent-icon">🧠</div><div class="agent-name">Analysis Agent</div><div class="agent-desc">AI insights & synthesis</div></div>
    <div class="agent-card"><div class="agent-icon">📧</div><div class="agent-name">Mail Agent</div><div class="agent-desc">Email drafting & scheduling</div></div>
    <div class="agent-card"><div class="agent-icon">📅</div><div class="agent-name">Calendar Agent</div><div class="agent-desc">Meeting scheduling & time blocking</div></div>
   </div>
  </div>

  <div id="resultsContainer" class="hidden">
   <h2>🎯 Orchestration Results</h2>
   <div id="agentProgress"></div>
   <div id="finalResults"></div>
  </div>
 </main>
</div>

<script>
function setExample(t){document.getElementById('queryInput').value=t}
async function executeOrchestration(){
 const q=document.getElementById('queryInput').value.trim();
 const btn=document.getElementById('executeBtn');
 if(!q){alert('Enter a query');return}
 btn.textContent='🔄 Orchestrating...';btn.disabled=true;
 document.getElementById('resultsContainer').classList.remove('hidden');
 document.getElementById('agentProgress').innerHTML='<div class="agent-step executing">🚀 Initializing...</div>';
 document.getElementById('finalResults').innerHTML='';
 const fd=new FormData();fd.append('query',q);
 [...document.getElementById('fileInput').files].forEach(f=>fd.append('files',f));
 try{
  const r=await fetch('/execute',{method:'POST',body:fd});
  const d=await r.json();
  if(!d.success) throw new Error(d.error||'Unknown');
  document.getElementById('finalResults').innerHTML='<pre style="white-space:pre-wrap">'+JSON.stringify(d.data,null,2)+'</pre>';
 }catch(e){
  document.getElementById('finalResults').innerHTML='<div class="result-section" style="border-color:#f44336"><h4>❌ Error</h4><p>'+e.message+'</p></div>';
 }finally{btn.textContent='🚀 Execute Orchestration';btn.disabled=false;}
}
</script>
</body>
</html>"""
