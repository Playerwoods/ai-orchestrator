from typing import Dict, Any, List, Optional, Union
import asyncio
import traceback
from datetime import datetime
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base class for all agents with guaranteed response structure"""
    
    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        """Check if this agent can handle the given task type"""
        pass
    
    @abstractmethod
    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Agent-specific task execution logic"""
        pass
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with guaranteed response structure"""
        try:
            # Execute the agent-specific logic
            result = await self._execute_task(task)
            
            # Ensure we have a summary
            if not result.get("summary"):
                result["summary"] = self._generate_default_summary(task, result)
            
            # Ensure we have a status
            if not result.get("status"):
                result["status"] = "completed"
            
            return result
            
        except Exception as e:
            error_msg = f"Error in {self.__class__.__name__}: {str(e)}"
            return {
                "status": "error",
                "summary": error_msg,
                "message": str(e),
                "details": traceback.format_exc()
            }
    
    def _generate_default_summary(self, task: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Generate a default summary if none provided"""
        task_type = task.get("task_type", "task")
        return f"Successfully completed {task_type} task"


class SpotlightAgent(BaseAgent):
    def can_handle(self, task_type: str) -> bool:
        return task_type == "spotlight_search"
    
    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", "")
        # Simulate spotlight search
        await asyncio.sleep(0.1)
        return {
            "summary": f"Searched system for '{query}' and found 5 relevant items",
            "results": {"items_found": 5, "query": query}
        }


class FileAgent(BaseAgent):
    def can_handle(self, task_type: str) -> bool:
        return task_type == "file_processing"
    
    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        files = task.get("files", [])
        
        if not files:
            return {
                "status": "error",
                "summary": "No files provided for processing"
            }
        
        # Simulate file processing
        await asyncio.sleep(0.2)
        
        file_names = files if isinstance(files, list) else [files]
        extracted_text = f"Extracted content from {len(file_names)} file(s)"
        
        return {
            "summary": f"Successfully processed {len(file_names)} file(s)",
            "results": {
                "extracted_text": extracted_text,
                "file_count": len(file_names),
                "files_processed": file_names
            }
        }


class ResearchAgent(BaseAgent):
    def can_handle(self, task_type: str) -> bool:
        return task_type == "web_research"
    
    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", task.get("text_content", ""))
        
        # Simulate web research
        await asyncio.sleep(0.3)
        
        research_results = {
            "sources": ["Source 1", "Source 2", "Source 3"],
            "key_findings": [
                "AI automation market growing at 30% CAGR",
                "Key players include Microsoft, Google, Amazon",
                "Market size expected to reach $50B by 2025"
            ]
        }
        
        return {
            "summary": f"Researched '{query}' and found {len(research_results['sources'])} relevant sources with key market insights",
            "results": research_results
        }


class AnalysisAgent(BaseAgent):
    def can_handle(self, task_type: str) -> bool:
        return task_type == "analysis"
    
    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        text_content = task.get("text_content", task.get("query", ""))
        
        if not text_content:
            return {
                "status": "error",
                "summary": "No content provided for analysis"
            }
        
        # Simulate analysis
        await asyncio.sleep(0.2)
        
        # Check if this is from previous research
        if "key_findings" in str(task):
            summary = "Created comprehensive competitive analysis report based on research findings. The AI automation market shows strong growth with major tech companies leading innovation."
        else:
            word_count = len(text_content.split())
            summary = f"Analyzed content ({word_count} words) and identified key themes and insights"
        
        return {
            "summary": summary,
            "results": {
                "analysis_type": "competitive_analysis" if "research" in text_content.lower() else "general_analysis",
                "confidence": 0.85
            }
        }


class MailAgent(BaseAgent):
    def can_handle(self, task_type: str) -> bool:
        return task_type == "email_analysis"
    
    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate email analysis
        await asyncio.sleep(0.1)
        return {
            "summary": "Analyzed email inbox and found 10 important messages requiring attention",
            "results": {"important_emails": 10}
        }


class CalendarAgent(BaseAgent):
    def can_handle(self, task_type: str) -> bool:
        return task_type == "schedule_meeting"
    
    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate calendar scheduling
        await asyncio.sleep(0.1)
        return {
            "summary": "Found 3 available time slots for the requested meeting",
            "results": {"available_slots": 3}
        }


class MultiAgentOrchestrator:
    """Orchestrator that guarantees proper response structure"""
    
    def __init__(self):
        self.agents = {
            "spotlight": SpotlightAgent(),
            "file": FileAgent(),
            "research": ResearchAgent(),
            "analysis": AnalysisAgent(),
            "mail": MailAgent(),
            "calendar": CalendarAgent()
        }
    
    def find_capable_agents(self, task_type: str) -> List[str]:
        """Find agents capable of handling the task type"""
        return [name for name, agent in self.agents.items() 
                if agent.can_handle(task_type)]
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task with proper error handling"""
        task_type = task.get("task_type", "")
        
        if not task_type:
            return {
                "status": "error",
                "summary": "No task type specified",
                "message": "Task must include a 'task_type' field"
            }
        
        capable_agents = self.find_capable_agents(task_type)
        
        if not capable_agents:
            return {
                "status": "error",
                "summary": f"No agent available for task type: {task_type}",
                "message": f"Task type '{task_type}' is not supported"
            }
        
        agent_name = capable_agents[0]
        agent = self.agents[agent_name]
        
        try:
            result = await agent.execute(task)
            
            # Add orchestrator metadata
            if "orchestrator_info" not in result:
                result["orchestrator_info"] = {}
            
            result["orchestrator_info"].update({
                "selected_agent": agent_name,
                "task_type": task_type,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "summary": f"Agent '{agent_name}' failed: {str(e)}",
                "message": str(e),
                "details": traceback.format_exc(),
                "agent": agent_name,
                "task_type": task_type
            }
    
    def _determine_intent(self, query: str, has_files: bool) -> List[Dict[str, Any]]:
        """Determine the execution plan based on query analysis"""
        if not query:
            query = ""
        
        query_lower = query.lower().strip()
        plan = []
        
        # Keywords for different intents
        file_keywords = ["pdf", "document", "file", "doc", "txt", "attachment", "upload"]
        analysis_keywords = ["summarize", "summary", "analyze", "analysis", "insights", 
                           "report", "explain", "key points", "brief", "overview"]
        research_keywords = ["research", "google", "search web", "find information", 
                           "look up", "market", "competitive", "industry"]
        email_keywords = ["email", "mail", "inbox", "messages"]
        calendar_keywords = ["schedule", "meeting", "calendar", "appointment"]
        
        # Check for file-related requests without files
        mentions_file = any(keyword in query_lower for keyword in file_keywords)
        wants_analysis = any(keyword in query_lower for keyword in analysis_keywords)
        wants_research = any(keyword in query_lower for keyword in research_keywords)
        
        # Validation checks
        if mentions_file and not has_files:
            return [{
                "task_type": "error",
                "message": "You mentioned a file but didn't upload any. Please attach a file and try again."
            }]
        
        # Build execution plan
        if has_files:
            plan.append({"task_type": "file_processing"})
            if wants_analysis or not query:  # Default to analysis for files
                plan.append({"task_type": "analysis"})
        
        elif wants_research:
            plan.append({"task_type": "web_research"})
            if wants_analysis or "report" in query_lower:
                plan.append({"task_type": "analysis"})
        
        elif wants_analysis:
            # Check if there's enough content to analyze
            content_words = [w for w in query_lower.split() 
                           if w not in analysis_keywords + ["the", "a", "an", "this", "that"]]
            if len(content_words) < 3:
                return [{
                    "task_type": "error",
                    "message": "Please provide more content to analyze, or upload a file."
                }]
            plan.append({"task_type": "analysis"})
        
        elif any(keyword in query_lower for keyword in email_keywords):
            plan.append({"task_type": "email_analysis"})
        
        elif any(keyword in query_lower for keyword in calendar_keywords):
            plan.append({"task_type": "schedule_meeting"})
        
        else:
            # Default to analysis if query has substance
            if len(query.split()) > 3:
                plan.append({"task_type": "analysis"})
            else:
                return [{
                    "task_type": "error",
                    "message": "I couldn't understand what you'd like me to do. Please provide more details."
                }]
        
        return plan
    
    async def execute_orchestration(self, task: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Main orchestration method with guaranteed response structure"""
        try:
            # Normalize input
            if isinstance(task, str):
                task_dict = {"query": task}
            elif isinstance(task, dict):
                task_dict = task.copy()
            else:
                return self._error_response(
                    "Invalid input type",
                    f"Expected string or dict, got {type(task)}",
                    query=str(task)
                )
            
            query = task_dict.get("query", "")
            files = task_dict.get("files")
            
            # Create execution plan
            plan = self._determine_intent(query, bool(files))
            
            # Handle error plans
            if plan and plan[0].get("task_type") == "error":
                return self._error_response(
                    plan[0].get("message", "Invalid request"),
                    "Request validation failed",
                    query=query
                )
            
            # Execute plan
            agents_executed = []
            execution_context = task_dict.copy()
            final_summary_parts = []
            
            for i, step in enumerate(plan):
                task_type = step["task_type"]
                
                # Prepare task for current step
                current_task = execution_context.copy()
                current_task["task_type"] = task_type
                
                # Special handling for analysis tasks
                if task_type == "analysis":
                    # Use extracted text from files or original query
                    current_task["text_content"] = execution_context.get("extracted_text", query)
                
                # Execute task
                result = await self.execute_task(current_task)
                
                # Track execution
                agent_name = result.get("orchestrator_info", {}).get("selected_agent", "unknown")
                agents_executed.append(agent_name)
                
                # Collect summary
                if result.get("summary"):
                    final_summary_parts.append(result["summary"])
                
                # Handle errors
                if result.get("status") == "error":
                    return self._error_response(
                        result.get("summary", "Task failed"),
                        result.get("message", "Unknown error"),
                        query=query,
                        agents_executed=agents_executed,
                        failed_step=i + 1,
                        plan=plan
                    )
                
                # Update context with results
                if result.get("results"):
                    execution_context.update(result["results"])
            
            # Build final summary
            if final_summary_parts:
                final_summary = " ".join(final_summary_parts)
            else:
                final_summary = f"Completed {len(agents_executed)} task(s) successfully"
            
            return {
                "status": "completed",
                "summary": final_summary,
                "query": query,
                "agents_executed": agents_executed,
                "orchestration_metadata": {
                    "plan": plan,
                    "agents_executed": agents_executed,
                    "was_chained": len(agents_executed) > 1,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return self._error_response(
                "Orchestration failed",
                str(e),
                query=task_dict.get("query", "") if isinstance(task_dict, dict) else str(task)
            )
    
    def _error_response(self, summary: str, message: str, **kwargs) -> Dict[str, Any]:
        """Create a consistent error response"""
        response = {
            "status": "error",
            "summary": summary,
            "message": message,
            "query": kwargs.get("query", ""),
            "agents_executed": kwargs.get("agents_executed", [])
        }
        
        # Add any additional metadata
        if any(k for k in kwargs if k not in ["query", "agents_executed"]):
            response["orchestration_metadata"] = {
                k: v for k, v in kwargs.items() 
                if k not in ["query", "agents_executed"]
            }
        
        return response


# Example usage and testing
async def test_orchestrator():
    orchestrator = MultiAgentOrchestrator()
    
    test_cases = [
        # Test 1: Research and analysis
        {
            "query": "Research AI automation market and create competitive analysis report"
        },
        # Test 2: File request without file
        {
            "query": "read and summarize pdf"
        },
        # Test 3: Simple analysis
        {
            "query": "Analyze this text: The quick brown fox jumps over the lazy dog"
        },
        # Test 4: With file
        {
            "query": "summarize this document",
            "files": ["document.pdf"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n=== Test Case {i} ===")
        result = await orchestrator.execute_orchestration(test)
        print(f"Query: {result['query']}")
        print(f"Status: {result['status']}")
        print(f"Summary: {result['summary']}")
        print(f"Agents: {result['agents_executed']}")
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(test_orchestrator())
