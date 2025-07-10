from typing import Dict, Any, List, Union
import asyncio
from datetime import datetime
import PyPDF2


class MultiAgentOrchestrator:
    """Simple orchestrator that routes tasks to appropriate agents"""
    
    async def process_file(self, files: List[str]) -> Dict[str, Any]:
        """Process PDF files and extract text"""
        if not files:
            return {
                "status": "error",
                "summary": "No files provided"
            }
        
        all_text = []
        for file_path in files:
            try:
                with open(file_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    all_text.append(text.strip())
            except Exception as e:
                return {
                    "status": "error",
                    "summary": f"Failed to read PDF: {str(e)}"
                }
        
        combined_text = "\n\n".join(all_text)
        return {
            "status": "completed",
            "summary": f"Extracted text from {len(files)} file(s)",
            "extracted_text": combined_text
        }
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Simple text analysis without NLTK"""
        if not text:
            return {
                "status": "error",
                "summary": "No text to analyze"
            }
        
        # Simple analysis
        words = text.split()
        word_count = len(words)
        
        # Create a simple summary (first 100 words)
        summary_words = words[:100] if word_count > 100 else words
        short_summary = " ".join(summary_words)
        if word_count > 100:
            short_summary += "..."
        
        return {
            "status": "completed",
            "summary": f"Analyzed {word_count} words: {short_summary[:200]}..."
        }
    
    async def research_topic(self, query: str) -> Dict[str, Any]:
        """Simulate web research"""
        await asyncio.sleep(0.1)  # Simulate API call
        
        return {
            "status": "completed",
            "summary": f"Researched '{query}' - Found information about market trends, key players, and growth projections",
            "findings": [
                "Market growing at 30% annually",
                "Major players: Microsoft, Google, Amazon",
                "Expected to reach $50B by 2025"
            ]
        }
    
    def determine_task_type(self, query: str, has_files: bool) -> str:
        """Simple task type detection"""
        if not query:
            query = ""
        
        query_lower = query.lower()
        
        # Check for file processing
        if has_files:
            return "file_and_analyze"
        
        # Check for research
        if any(word in query_lower for word in ["research", "find", "search", "look up"]):
            return "research"
        
        # Check for analysis
        if any(word in query_lower for word in ["analyze", "summarize", "summary"]):
            if "pdf" in query_lower or "file" in query_lower or "document" in query_lower:
                return "need_file"
            return "analyze"
        
        # Default
        return "analyze" if len(query.split()) > 5 else "unclear"
    
    async def execute_orchestration(self, task: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Main orchestration method"""
        # Normalize input
        if isinstance(task, str):
            query = task
            files = None
        else:
            query = task.get("query", "")
            files = task.get("files")
        
        # Determine what to do
        task_type = self.determine_task_type(query, bool(files))
        
        # Handle different task types
        if task_type == "need_file":
            return {
                "status": "error",
                "summary": "You mentioned a file but didn't upload any. Please attach a file.",
                "query": query,
                "agents_executed": []
            }
        
        elif task_type == "unclear":
            return {
                "status": "error",
                "summary": "I couldn't understand your request. Please provide more details.",
                "query": query,
                "agents_executed": []
            }
        
        elif task_type == "file_and_analyze":
            # Process file first
            file_result = await self.process_file(files)
            if file_result["status"] == "error":
                return {
                    "status": "error",
                    "summary": file_result["summary"],
                    "query": query,
                    "agents_executed": ["file"]
                }
            
            # Then analyze the extracted text
            analysis_result = await self.analyze_text(file_result["extracted_text"])
            return {
                "status": "completed",
                "summary": f"{file_result['summary']}. {analysis_result['summary']}",
                "query": query,
                "agents_executed": ["file", "analysis"]
            }
        
        elif task_type == "research":
            # Do research
            research_result = await self.research_topic(query)
            
            # If they want a report, add analysis
            if "report" in query.lower() or "analysis" in query.lower():
                findings_text = "\n".join(research_result.get("findings", []))
                analysis_result = await self.analyze_text(f"{query}\n\nFindings:\n{findings_text}")
                return {
                    "status": "completed",
                    "summary": f"{research_result['summary']}. Created analysis report.",
                    "query": query,
                    "agents_executed": ["research", "analysis"]
                }
            
            return {
                "status": "completed",
                "summary": research_result["summary"],
                "query": query,
                "agents_executed": ["research"]
            }
        
        elif task_type == "analyze":
            # Direct text analysis
            analysis_result = await self.analyze_text(query)
            return {
                "status": "completed",
                "summary": analysis_result["summary"],
                "query": query,
                "agents_executed": ["analysis"]
            }
        
        # Fallback
        return {
            "status": "error",
            "summary": "Unable to process request",
            "query": query,
            "agents_executed": []
        }


# Testing
async def test_orchestrator():
    orchestrator = MultiAgentOrchestrator()
    
    # Test 1: Research request
    print("\n=== Test 1: Research ===")
    result = await orchestrator.execute_orchestration(
        "Research AI automation market and create competitive analysis report"
    )
    print(f"Status: {result['status']}")
    print(f"Summary: {result['summary']}")
    print(f"Agents: {result['agents_executed']}")
    
    # Test 2: File without upload
    print("\n=== Test 2: Missing File ===")
    result = await orchestrator.execute_orchestration("read and summarize pdf")
    print(f"Status: {result['status']}")
    print(f"Summary: {result['summary']}")
    
    # Test 3: Simple analysis
    print("\n=== Test 3: Text Analysis ===")
    result = await orchestrator.execute_orchestration(
        "Analyze this text: The quick brown fox jumps over the lazy dog"
    )
    print(f"Status: {result['status']}")
    print(f"Summary: {result['summary']}")


if __name__ == "__main__":
    asyncio.run(test_orchestrator())
