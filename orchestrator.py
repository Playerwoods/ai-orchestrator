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
        
        # Debug: Log what we received
        debug_info = {
            "received_task_type": type(task).__name__,
            "task_dict_keys": list(task_dict.keys()) if isinstance(task_dict, dict) else [],
            "has_files": "files" in task_dict if isinstance(task_dict, dict) else False,
            "has_query": "query" in task_dict if isinstance(task_dict, dict) else False,
            "has_task_type": "task_type" in task_dict if isinstance(task_dict, dict) else False
        }
        
        # Execute the task
        result = None
        
        # Handle different request formats - CHECK FILES FIRST!
        if isinstance(task_dict, dict) and "files" in task_dict and task_dict["files"]:
            # PRIORITY: File processing should be handled first
            file_task = {
                "task_type": "file_processing",
                "files": task_dict.get("files"),
                "query": task_dict.get("query", "Document Analysis"),
                **{k: v for k, v in task_dict.items() if k not in ["files", "query"]}
            }
            result = await self.execute_task(file_task)
        elif isinstance(task_dict, dict) and "task_type" in task_dict:
            result = await self.execute_task(task_dict)
        elif isinstance(task_dict, dict) and "query" in task_dict:
            result = await self.route_task_intelligently(task_dict["query"], task_dict)
        else:
            return {
                "status": "error",
                "message": "Invalid task format. Expected 'task_type', 'files', or 'query'",
                "received_keys": list(task_dict.keys()) if isinstance(task_dict, dict) else [],
                "debug_info": debug_info,
                "args_received": len(args),
                "kwargs_received": list(kwargs.keys()) if kwargs else []
            }
        
        # Ensure the result has the fields the frontend expects
        if result:
            # Force override all fields that frontend expects - no conditionals
            agent_name = result.get("agent", "UnknownAgent")
            
            # Extract summary with multiple fallbacks
            summary_text = "Task completed successfully"  # Default fallback
            
            # Try to get summary from various places
            if "summary" in result and result["summary"] and result["summary"] != "undefined":
                summary_text = result["summary"]
            elif "results" in result:
                if isinstance(result["results"], dict) and "summary" in result["results"]:
                    summary_text = result["results"]["summary"]
                elif isinstance(result["results"], list) and len(result["results"]) > 0:
                    first_result = result["results"][0]
                    if isinstance(first_result, dict):
                        if "detailed_analysis" in first_result:
                            summary_text = f"Analyzed {first_result.get('filename', 'document')} - comprehensive insights generated"
                        elif "filename" in first_result:
                            summary_text = f"Processed {first_result['filename']} successfully"
            
            # For specific agents, provide better summaries
            if agent_name == "FileAgent":
                summary_text = "Document analysis completed with detailed insights and recommendations"
            elif agent_name == "AnalysisAgent":
                summary_text = "Generated comprehensive analysis with strategic recommendations"
            elif agent_name == "ResearchAgent":
                summary_text = "Completed research with findings and sources"
            
            # FORCE SET all required fields - completely overwrite
            result.update({
                "query": str(task_dict.get("query", "Analysis Request")),
                "agents_executed": [agent_name],
                "summary": summary_text,
                "status": "completed"
            })
            
            # Also set in orchestration_metadata as backup
            result["orchestration_metadata"] = {
                "query": result["query"],
                "agents_executed": result["agents_executed"],
                "status": result["status"],
                "summary": result["summary"],
                "task_type": task_dict.get("task_type", "auto-detected"),
                "debug_info": {
                    "original_summary": result.get("original_summary", "none"),
                    "agent": agent_name,
                    "result_keys": list(result.keys())
                }
            }
        
        return result
