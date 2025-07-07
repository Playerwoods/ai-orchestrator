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
    # VVVVVV CORE LOGIC: This method contains the definitive fix VVVVVVV
    # ========================================================================
    def _determine_intent(self, query: str, has_files: bool) -> List[Dict[str, Any]]:
        """
        Determines the sequence of tasks (a plan). This version checks for
        query substance before creating an analysis plan.
        """
        query_lower = query.lower().strip() if query else ""
        plan = []

        # --- INTENT KEYWORDS ---
        file_keywords = ["pdf", "document", "file", "doc", "txt", "attachment"]
        analysis_keywords = ["summarize", "summary", "analyze", "insights", "report", "explain", "key points"]
        research_keywords = ["research", "google", "search web", "find information on", "look up"]
        
        # --- LOGIC ---
        
        # 1. Check for invalid file-related queries
        if any(keyword in query_lower for keyword in file_keywords) and not has_files:
            return [{"task_type": "error", "message": "You mentioned a document, but no file was attached. Please upload a file."}]

        # 2. Check for analysis requests that lack substance
        is_analysis_request = any(keyword in query_lower for keyword in analysis_keywords)
        if is_analysis_request and not has_files:
            # Check if the query is ONLY command words (e.g., "summarize", "analyze report")
            query_words = set(query_lower.split())
            command_words = set(analysis_keywords + ["the", "a", "an"]) # Add common articles
            if query_words.issubset(command_words):
                return [{"task_type": "error", "message": "You asked to summarize or analyze, but didn't provide enough text or a file. Please provide more content."}]

        # 3. Build the valid plan
        if has_files:
            plan.append({"task_type": "file_processing"})
            if is_analysis_request or not query_lower:
                 plan.append({"task_type": "analysis"})
        elif is_analysis_request:
            # The query has substance and no file, so analyze the query text
            plan.append({"task_type": "analysis"})
        elif any(keyword in query_lower for keyword in research_keywords):
            plan.append({"task_type": "web_research"})
        
        # 4. Default to analysis for generic queries with substance
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
            return {"status": "error", "summary": f"Invalid input type: {type(task)}", "query": str(task), "agents_executed": []}

        query = task_dict.get("query", "")
        files = task_dict.get("files")
        
        # 2. Create a Dynamic Plan
        plan = self._determine_intent(query, bool(files))
        print(f"Orchestrator created plan: {plan}")

        # Handle error plans from the intent detector (e.g., missing file, no substance)
        if not plan or (plan[0].get("task_type") == "error"):
            error_message = plan[0].get("message") if plan else "I'm sorry, I could not understand your request."
            return {
                "status": "error",
                "summary": error_message,
                "query": query,
                "agents_executed": [],
                "orchestration_metadata": {"plan": plan, "agents_executed": []}
            }

        # 3. Execute the Plan
        agents_executed = []
        execution_context = task_dict 

        for i, step in enumerate(plan):
            current_task_type = step["task_type"]
            print(f"\n--- Executing Step {i+1}/{len(plan)}: Agent for '{current_task_type}' ---")

            current_task = execution_context.copy()
            current_task["task_type"] = current_task_type

            if current_task_type == "analysis":
                current_task["text_content"] = execution_context.get("extracted_text", query)

            step_result = await self.execute_task(current_task)

            if step_result.get("results"):
                 execution_context.update(step_result["results"])
            
            execution_context["summary"] = step_result.get("summary", execution_context.get("summary"))
            execution_context["status"] = step_result.get("status")
            
            agent_name = step_result.get("orchestrator_info", {}).get("selected_agent")
            if agent_name:
                agents_executed.append(agent_name)
            
            if execution_context["status"] == "error":
                print(f"--- Step Failed ---")
                error_summary = step_result.get("message", "An unknown error occurred.")
                return {
                    "status": "error",
                    "summary": f"Error during '{current_task_type}': {error_summary}",
                    "query": query,
                    "agents_executed": agents_executed,
                    "orchestration_metadata": {"plan": plan, "failed_step": i + 1, "error_details": step_result}
                }
            
            print(f"--- Step {i+1} Completed. Agent: {agent_name} ---")

        # 4. Finalize the Response
        print("\n--- Orchestration Complete ---")
        final_summary = execution_context.get("summary", "Task completed, but no summary was generated.")

        return {
            "status": "completed",
            "summary": final_summary,
            "query": query,
            "agents_executed": agents_executed,
            "orchestration_metadata": {"plan": plan, "agents_executed": agents_executed, "was_chained": len(agents_executed) > 1}
        }
        
    def _get_all_task_types(self) -> Dict[str, List[str]]:
        # This method is not directly used by the new orchestrator but is good to keep for status checks
        return {
            "spotlight": ["spotlight_search"],
            "file": ["file_processing"],
            "research": ["web_research"],
            "analysis": ["analysis"],
            "mail": ["email_analysis"],
            "calendar": ["schedule_meeting"]
        }
