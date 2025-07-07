from typing import Dict, Any, List
import asyncio

# Import all agent classes
from agents import (
    BaseAgent,
    SpotlightAgent,
    FileAgent,
    ResearchAgent,
    AnalysisAgent,
    MailAgent,
    CalendarAgent
)

class MultiAgentOrchestrator:
    def __init__(self):
        self.agents = {
            "spotlight": SpotlightAgent(),
            "file": FileAgent(),
            "research": ResearchAgent(),
            "analysis": AnalysisAgent(),
            "mail": MailAgent(),
            "calendar": CalendarAgent()
        }
    
    def get_available_agents(self) -> Dict[str, Any]:
        """Return detailed info about available agents."""
        import sys
        
        agents_info = {}
        active_count = 0
        
        for name, agent in self.agents.items():
            available = True
            status = "active"
            
            # Check platform compatibility
            if name == "spotlight" and sys.platform != "darwin":
                available = False
                status = "unavailable (macOS only)"
            
            if available:
                active_count += 1
            
            agents_info[name] = {
                "class": agent.__class__.__name__,
                "status": status,
                "available": available
            }
        
        return {
            "total_defined": len(self.agents),
            "active_agents": active_count,
            "agents": agents_info,
            "platform": sys.platform
        }
    
    def find_capable_agents(self, task_type: str) -> List[str]:
        capable_agents = []
        for name, agent in self.agents.items():
            if agent.can_handle(task_type):
                capable_agents.append(name)
        return capable_agents
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("task_type", "")
        
        if not task_type:
            return {
                "status": "error",
                "message": "No task_type specified",
                "available_task_types": self._get_all_task_types()
            }
        
        capable_agents = self.find_capable_agents(task_type)
        
        if not capable_agents:
            return {
                "status": "error",
                "message": f"No agent found capable of handling task type: {task_type}",
                "available_task_types": self._get_all_task_types()
            }
        
        agent_name = capable_agents[0]
        agent = self.agents[agent_name]
        
        try:
            result = await agent.execute(task)
            result["orchestrator_info"] = {
                "selected_agent": agent_name,
                "capable_agents": capable_agents,
                "task_type": task_type
            }
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Agent {agent_name} failed to execute task: {str(e)}",
                "agent": agent_name,
                "task_type": task_type
            }
    
    async def execute_multi_agent_task(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = await asyncio.gather(
            *[self.execute_task(task) for task in tasks],
            return_exceptions=True
        )
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "status": "error",
                    "message": f"Task {i} failed: {str(result)}",
                    "task_index": i
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _get_all_task_types(self) -> Dict[str, List[str]]:
        agent_capabilities = {
            "spotlight": ["spotlight_search"],
            "file": ["file_processing", "pdf_analysis", "document_extraction"],
            "research": ["web_research", "competitor_analysis", "market_research", "safari_research"],
            "analysis": ["analysis", "insights", "summary", "report_generation"],
            "mail": ["email_analysis", "draft_email", "schedule_email", "email_insights", "extract_action_items"],
            "calendar": ["schedule_meeting", "find_availability", "meeting_prep", "calendar_insights", "time_blocking"]
        }
        
        return agent_capabilities
    
    async def get_agent_status(self) -> Dict[str, Any]:
        status = {
            "total_agents": len(self.agents),
            "agents": {},
            "capabilities": self._get_all_task_types()
        }
        
        active_agents = 0
        
        for name, agent in self.agents.items():
            # Check if agent is platform-compatible
            available = True
            platform_note = ""
            
            if name == "spotlight":
                import sys
                if sys.platform != "darwin":
                    available = False
                    platform_note = "macOS only - not available on current platform"
                else:
                    platform_note = "macOS native integration"
            
            if available:
                active_agents += 1
            
            status["agents"][name] = {
                "class": agent.__class__.__name__,
                "available": available,
                "platform_note": platform_note if platform_note else "Cross-platform compatible"
            }
        
        status["active_agents"] = active_agents
        status["platform_info"] = {
            "current_platform": __import__('sys').platform,
            "spotlight_available": __import__('sys').platform == "darwin"
        }
        
        return status
    
    async def route_task_intelligently(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        context = context or {}
        
        routing_keywords = {
            "spotlight_search": ["find file", "search file", "locate document", "spotlight"],
            "file_processing": ["analyze pdf", "extract text", "document analysis", "read document"],
            "web_research": ["research", "google", "search web", "find information"],
            "email_analysis": ["email", "draft email", "mail", "inbox"],
            "schedule_meeting": ["schedule", "meeting", "calendar", "appointment"],
            "analysis": ["analyze", "insights", "summary", "report"]
        }
        
        task_type = None
        query_lower = query.lower()
        
        for task, keywords in routing_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                task_type = task
                break
        
        if not task_type:
            task_type = "analysis"
        
        task = {
            "task_type": task_type,
            "query": query,
            **context
        }
        
        return await self.execute_task(task)
    
    async def execute_orchestration(self, task, *args, **kwargs) -> Dict[str, Any]:
        """
        Main orchestration method that the frontend calls.
        This is the entry point for all task execution.
        Handles variable arguments and input types for backward compatibility.
        """
        # Handle different input types
        if isinstance(task, str):
            # If task is a string, treat it as a query
            task_dict = {"query": task}
        elif isinstance(task, dict):
            # If task is already a dictionary, use it as is
            task_dict = task
        else:
            # Handle other types
            return {
                "status": "error",
                "message": f"Invalid task type. Expected dict or str, got {type(task)}",
                "task_type": str(type(task))
            }
        
        # Handle different request formats for backward compatibility
        
        # If it's a direct task, execute it
        if "task_type" in task_dict:
            return await self.execute_task(task_dict)
        
        # Handle file processing requests
        if "files" in task_dict:
            # Auto-detect this is a file processing task
            file_task = {
                "task_type": "file_processing",
                "files": task_dict.get("files"),
                "query": task_dict.get("query", ""),
                **task_dict  # Include any other parameters
            }
            return await self.execute_task(file_task)
        
        # Handle query-based requests
        if "query" in task_dict:
            return await self.route_task_intelligently(task_dict["query"], task_dict)
        
        # Fallback for unrecognized format
        return {
            "status": "error",
            "message": "Invalid task format. Expected 'task_type', 'files', or 'query'",
            "received_keys": list(task_dict.keys()),
            "args_received": len(args),
            "kwargs_received": list(kwargs.keys()) if kwargs else []
        }
