from typing import Dict, Any, List
import asyncio
import sys

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
    
    def find_capable_agents(self, task_type: str) -> List[str]:
        capable_agents = []
        for name, agent in self.agents.items():
            if agent.can_handle(task_type):
                capable_agents.append(name)
        return capable_agents
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("task_type", "")
        if not task_type:
            return {"status": "error", "message": "No task_type specified"}
        
        capable_agents = self.find_capable_agents(task_type)
        if not capable_agents:
            return {"status": "error", "message": f"No agent found for task: {task_type}"}
        
        agent_name = capable_agents[0]
        agent = self.agents[agent_name]
        
        try:
            result = await agent.execute(task)
            # Add orchestrator info without overwriting existing keys
            if "orchestrator_info" not in result:
                result["orchestrator_info"] = {}
            result["orchestrator_info"].update({
                "selected_agent": agent_name,
                "task_type": task_type
            })
            return result
        except Exception as e:
            # Provide more detailed error logging
            import traceback
            error_details = traceback.format_exc()
            return {
                "status": "error",
                "message": f"Agent '{agent_name}' failed: {str(e)}",
                "agent": agent_name,
                "task_type": task_type,
                "details": error_details
            }
    
    def _determine_intent(self, query: str, has_files: bool) -> List[Dict[str, Any]]:
        """
        Determines the sequence of tasks (a plan) based on the user's query and context.
        This is the core of the "smarter" orchestrator.
        """
        query_lower = query.lower() if query else ""
        plan = []

        # --- Step 1: Handle File Input ---
        if has_files:
            plan.append({"task_type": "file_processing"})
        
        # --- Step 2: Determine Next Action based on Query Keywords ---
        analysis_keywords = ["summarize", "summary", "analyze", "insights", "report", "explain", "key points"]
        research_keywords = ["research", "google", "search web", "find information on", "look up"]
        email_keywords = ["email", "draft", "mail", "inbox"]
        calendar_keywords = ["schedule", "meeting", "calendar", "appointment"]

        if any(keyword in query_lower for keyword in analysis_keywords):
            # If there was a file, this analysis will use its content.
            # If not, it will analyze the query text itself.
            plan.append({"task_type": "analysis"})
        elif any(keyword in query_lower for keyword in research_keywords):
            plan.append({"task_type": "web_research"})
        elif any(keyword in query_lower for keyword in email_keywords):
            plan.append({"task_type": "email_analysis"}) # or draft_email, etc.
        elif any(keyword in query_lower for keyword in calendar_keywords):
            plan.append({"task_type": "schedule_meeting"})
        elif query and not plan:
            # If there's a query but no other intent matched, default to analysis.
            plan.append({"task_type": "analysis"})
        
        # If there are no files and no query, it's an invalid request.
        if not plan:
            return []
            
        return plan

    # ========================================================================
    # VVVVVV THIS IS THE FULLY REVISED, MORE POWERFUL ORCHESTRATOR VVVVVVVV
    # ========================================================================
    async def execute_orchestration(self, task: Any, *args, **kwargs) -> Dict[str, Any]:
        """
        Main orchestration method. It creates a dynamic plan and executes a chain of
        agents to fulfill the user's request.
        """
        # 1. Normalize Input
        if isinstance(task, str):
            task_dict = {"query": task}
        elif isinstance(task, dict):
            task_dict = task
        else:
            return {"status": "error", "message": f"Invalid task type: {type(task)}"}

        query = task_dict.get("query")
        files = task_dict.get("files")
        
        # 2. Create a Dynamic Plan
        plan = self._determine_intent(query, bool(files))
        
        if not plan:
            return {"status": "error", "message": "Could not determine intent. Please provide a query or a file."}

        # 3. Execute the Plan (Agent Chain)
        agents_executed = []
        # `last_result` will hold the data to be passed from one agent to the next.
        # Start with the initial user request.
        last_result = task_dict.copy()
        
        for i, step in enumerate(plan):
            # Prepare the task for the current agent in the chain
            current_task = {
                "task_type": step["task_type"],
                "query": query,
            }
            
            # --- CRITICAL: Pass data between agents ---
            # The FileAgent provides `extracted_text`. The AnalysisAgent needs it.
            if "extracted_text" in last_result:
                current_task["text_content"] = last_result["extracted_text"]
            
            # Pass files only to the file_processing agent
            if step["task_type"] == "file_processing":
                current_task["files"] = files

            # Execute the step
            step_result = await self.execute_task(current_task)
            
            # If any step in the chain fails, abort the entire plan.
            if step_result.get("status") == "error":
                step_result["orchestration_metadata"] = {
                    "plan": plan,
                    "failed_step": i + 1,
                    "agents_executed": agents_executed,
                }
                return step_result
            
            # Update agents_executed list and prepare data for the next step
            agents_executed.append(step_result.get("orchestrator_info", {}).get("selected_agent", "UnknownAgent"))
            
            # The output of this step becomes the input for the next.
            # We merge results, with newer results overwriting older ones.
            # IMPORTANT: Your agents must return results in a consistent format.
            # For example, FileAgent should return `{"extracted_text": "..."}`.
            last_result.update(step_result.get("results", {}))
            last_result["summary"] = step_result.get("summary") # Capture the most recent summary

        # 4. Finalize the Response
        final_summary = last_result.get("summary", "Task completed successfully.")
        
        final_response = {
            "status": "completed",
            "query": query,
            "summary": final_summary,
            # Return the actual data from the last agent
            "results": last_result, 
            "orchestration_metadata": {
                "plan": plan,
                "agents_executed": agents_executed,
                "was_chained": len(agents_executed) > 1
            }
        }
        
        return final_response

    # (Other methods like get_available_agents, etc., can remain as they were)
    # ... include the rest of your class methods here ...
