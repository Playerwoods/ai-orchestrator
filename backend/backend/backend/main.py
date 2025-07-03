from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from orchestrator import MultiAgentOrchestrator
app = FastAPI(
    title="AI Document Orchestrator",
    description="Multi-agent AI orchestration platform",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Initialize orchestrator
orchestrator = MultiAgentOrchestrator()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main frontend"""
    try:
        with open("frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Frontend not found</h1>")

@app.post("/execute")
async def execute_orchestration(
    query: str = Form(...),
    files: List[UploadFile] = File(default=[])
):
    """Main orchestration endpoint"""
    try:
        # Process uploaded files
        file_data = []
        for file in files:
            content = await file.read()
            file_data.append({
                "filename": file.filename,
                "content": content,
                "size": len(content),
                "content_type": file.content_type
            })
        
        # Execute orchestration
        result = await orchestrator.execute_orchestration(query, file_data)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agents": list(orchestrator.agents.keys())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
