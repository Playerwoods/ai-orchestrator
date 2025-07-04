# Add to orchestrator.py imports
from agents import FileAgent, ResearchAgent, AnalysisAgent, MailAgent, CalendarAgent

class MultiAgentOrchestrator:
    def __init__(self):
        self.agents = {
            "file": FileAgent(),
            "research": ResearchAgent(), 
            "analysis": AnalysisAgent(),
            "mail": MailAgent(),          # Add this
            "calendar": CalendarAgent()   # Add this
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
