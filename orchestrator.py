from typing import Dict, Any, List
import asyncio
import sys
import traceback

# Import all agent classes
# Make sure this path is correct for your project structure
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
            return {"status": "error", "message": "No task_type specified in task payload"}
        
        capable_agents = self.find_capable_agents(task_type)
        if not capable_agents:
            return {"status": "error", "message": f"No agent found for task type: {task_type}"}
        
        agent_name = capable_agents[0]
        agent = self.agents[agent_name]
        
        try:
            result = await agent.execute(task)
            if "orchestrator_info" not in result:
                result["orchestrator_info"] = {}
            result["orchestrator_info"].update({
                "selected_agent": agent_name,
                "task_type": task_type
            })
            return result
        except Exception as e:
            error_details = traceback.format_exc()
            return {
                "status": "error",
                "message": f"Agent '{agent_name}' threw an exception: {str(e)}",
                "agent": agent_name,
                "task_type": task_type,
                "details": error_details
            }

    # ========================================================================
    # VVVVVV CORE LOGIC: These two methods contain the definitive fix VVVVVVV
    # ========================================================================

    def _determine_intent(self, query: str, has_files: bool) -> List[Dict[str, Any]]:
        """
        Determines the sequence of tasks (a plan). This version is more robust
        and handles missing context gracefully.
        """
        query_lower = query.lower() if query else ""
        plan = []

        # --- INTENT KEYWORDS ---
        file_keywords = ["pdf", "document", "file", "doc", "txt", "attachment"]
        analysis_keywords = ["summarize", "summary", "analyze", "insights", "report", "explain", "key points"]
        research_keywords = ["research", "google", "search web", "find information on", "look up"]
        
        # --- LOGIC ---
        # **Critical Check:** If the query implies a file but none is provided, create an error plan.
        if any(keyword in query_lower for keyword in file_keywords) and not has_files:
            return [{"task_type": "error", "message": "You mentioned a document, but no file was attached. Please upload a file."}]

        # Step 1: Handle File Input
        if has_files:
            plan.append({"task_type": "file_processing"})
            # If the query asks for analysis or is generic, chain the AnalysisAgent.
            if any(keyword in query_lower for keyword in analysis_keywords) or not query_lower:
                 plan.append({"task_type": "analysis"})

        # Step 2: Handle other intents if no file-based plan was made
        if not plan: 
            if any(keyword in query_lower for keyword in analysis_keywords):
                # An analysis task without a file means analyzing the query text itself.
                plan.append({"task_type": "analysis"})
            elif any(keyword in query_lower for keyword in research_keywords):
                plan.append({"task_type": "web_research"})

        # Default to analysis if there is a query but no other plan was made
        if query and not plan:
            plan.append({"task_type": "analysis"})
            
        return plan

    async def execute_orchestration(self, task: Any, *args, **kwargs) -> Dict[str, Any]:
        """
        Main orchestration method. Creates a dynamic plan and executes a chain of
        agents, ensuring a consistently structured response, even on error.
        """
        print(f"Orchestrator received task: {task}")
        
        # 1. Normalize Input
        if isinstance(task, str):
            task_dict = {"query": task}
        elif isinstance(task, dict):
            task_dict = task.copy()
        else:
            return {"status": "error", "summary": f"Invalid input type: {type(task)}", "agents_executed": [], "query": str(task)}

        query = task_dict.get("query", "")
        files = task_dict.get("files")
        
        # 2. Create a Dynamic Plan
        plan = self._determine_intent(query, bool(files))
        print(f"Orchestrator created plan: {plan}")

        # Handle error plans created by the intent detector (e.g., missing file)
        if not plan or (plan[0].get("task_type") == "error"):
            error_message = plan[0].get("message") if plan else "I'm sorry, I could not understand your request."
            return {
                "status": "error",
                "summary": error_message,
                "query": query,
                "orchestration_metadata": {"plan": plan, "agents_executed": []}
            }

        # 3. Execute the Plan (Agent Chain)
        agents_executed = []
        execution_context = task_dict 

        for i, step in enumerate(plan):
            current_task_type = step["task_type"]
            print(f"\n--- Executing Step {i+1}/{len(plan)}: Agent for '{current_task_type}' ---")

            current_task = execution_context.copy()
            current_task["task_type"] = current_task_type

            # Pass extracted text to the analysis agent
            if current_task_type == "analysis":
                # If text was extracted from a file, use it. Otherwise, use the query itself.
                current_task["text_content"] = execution_context.get("extracted_text", query)

            step_result = await self.execute_task(current_task)

            # Merge results back into the context for the next agent
            if step_result.get("results"):
                 execution_context.update(step_result["results"])
            
            execution_context["summary"] = step_result.get("summary", execution_context.get("summary"))
            execution_context["status"] = step_result.get("status")
            
            agent_name = step_result.get("orchestrator_info", {}).get("selected_agent")
            if agent_name:
                agents_executed.append(agent_name)
            
            # If any step fails, abort and return a structured error response
            if execution_context["status"] == "error":
                print(f"--- Step Failed ---")
                error_summary = step_result.get("message", "An unknown error occurred.")
                return {
                    "status": "error",
                    "summary": f"Error during '{current_task_type}': {error_summary}",
                    "query": query,
                    "orchestration_metadata": {
                        "plan": plan,
                        "failed_step": i + 1,
                        "agents_executed": agents_executed,
                        "error_details": step_result
                    }
                }
            
            print(f"--- Step {i+1} Completed. Agent: {agent_name} ---")

        # 4. Finalize the Response
        print("\n--- Orchestration Complete ---")
        final_summary = execution_context.get("summary", "Task completed, but no summary was generated.")

        return {
            "status": "completed",
            "summary": final_summary,
            "query": query,
            "agents_executed": agents_executed, # Top-level for easy access
            "orchestration_metadata": {
                "plan": plan,
                "agents_executed": agents_executed,
                "was_chained": len(agents_executed) > 1,
                "final_context": execution_context
            }
        }
        
    # Other helper methods can be included below
    def _get_all_task_types(self) -> Dict[str, List[str]]:
        return {
            "spotlight": ["spotlight_search"],
            "file": ["file_processing", "pdf_analysis", "document_extraction"],
            "research": ["web_research", "competitor_analysis", "market_research", "safari_research"],
            "analysis": ["analysis", "insights", "summary", "report_generation"],
            "mail": ["email_analysis", "draft_email", "schedule_email", "email_insights"],
            "calendar": ["schedule_meeting", "find_availability", "meeting_prep", "calendar_insights"]
        }
