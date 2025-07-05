from typing import Dict, Any, List
from agents import FileAgent, ResearchAgent, AnalysisAgent, MailAgent, CalendarAgent
import asyncio

class MultiAgentOrchestrator:
    def __init__(self):
        self.agents = {
            "file": FileAgent(),
            "research": ResearchAgent(), 
            "analysis": AnalysisAgent(),
            "mail": MailAgent(),
            "calendar": CalendarAgent()
            "spotlight": SpotlightAgent()
        }
        
    def parse_user_intent(self, query: str) -> List[Dict[str, Any]]:
        """Convert natural language query into agent tasks"""
        tasks = []
        query_lower = query.lower()
        
        # Mail tasks
        if any(word in query_lower for word in ["email", "mail", "draft", "send", "action items"]):
            tasks.append({
                "agent_type": "mail",
                "task_type": "email_analysis",
                "priority": 1
            })
        
        # Calendar tasks  
        if any(word in query_lower for word in ["schedule", "meeting", "calendar", "available", "time"]):
            tasks.append({
                "agent_type": "calendar",
                "task_type": "schedule_meeting",
                "priority": 1
            })
        
        # File processing tasks
        if any(word in query_lower for word in ["pdf", "document", "file", "upload"]):
            tasks.append({
                "agent_type": "file",
                "task_type": "file_processing",
                "priority": 2
            })
        
        # Research tasks  
        if any(word in query_lower for word in ["research", "competitor", "market", "find"]):
            tasks.append({
                "agent_type": "research",
                "task_type": "web_research", 
                "priority": 3
            })
            
        # Analysis tasks
        if any(word in query_lower for word in ["analyze", "insights", "summary", "report"]):
            tasks.append({
                "agent_type": "analysis",
                "task_type": "analysis",
                "priority": 4
            })
            
        # If no specific tasks detected, default to analysis
        if not tasks:
            tasks.append({
                "agent_type": "analysis",
                "task_type": "analysis",
                "priority": 1
            })
            
        return sorted(tasks, key=lambda x: x["priority"])
    
    async def execute_orchestration(self, query: str, files: List[Dict] = None) -> Dict[str, Any]:
        """Main orchestration logic"""
        tasks = self.parse_user_intent(query)
        results = []
        context = {"query": query, "files": files or []}
        
        for task in tasks:
            agent_type = task["agent_type"]
            agent = self.agents.get(agent_type)
            
            if agent and agent.can_handle(task["task_type"]):
                # Prepare task data
                task_data = {
                    "query": query,
                    "task_type": task["task_type"],
                    "files": files or [],
                    "context": context
                }
                
                # Execute agent
                result = await agent.execute(task_data)
                results.append(result)
                
                # Update context for next agent
                context[f"{agent_type}_result"] = result
        
        return {
            "orchestration_id": "orch_" + str(hash(query))[:8],
            "query": query,
            "agents_executed": len(results),
            "agent_results": results,
            "final_summary": self.generate_summary(results),
            "status": "completed"
        }
    
    def generate_summary(self, results: List[Dict]) -> str:
        """Generate overall summary of orchestration"""
        if not results:
            return "No agents executed"
            
        agent_names = [r.get("agent", "Unknown") for r in results]
        return f"Successfully coordinated {len(results)} agents: {', '.join(agent_names)}"
