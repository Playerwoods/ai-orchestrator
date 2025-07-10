from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import tempfile
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
        # Process uploaded files and save them temporarily
        file_paths = []
        for file in files:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                file_paths.append(tmp_file.name)
        
        # Execute orchestration with a single dictionary argument
        result = await orchestrator.execute_orchestration({
            "query": query,
            "files": file_paths if file_paths else None
        })
        
        # Clean up temporary files
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except:
                pass
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        # Clean up files on error too
        if 'file_paths' in locals():
            for file_path in file_paths:
                try:
                    os.remove(file_path)
                except:
                    pass
        
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check if orchestrator has the simple methods (from the new simple version)
    agent_info = {
        "file_processing": hasattr(orchestrator, 'process_file'),
        "analysis": hasattr(orchestrator, 'analyze_text'),
        "research": hasattr(orchestrator, 'research_topic')
    }
    return {"status": "healthy", "capabilities": agent_info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
