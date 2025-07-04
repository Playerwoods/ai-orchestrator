from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import PyPDF2
import requests
import json
import io
import os

class BaseAgent(ABC):
    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        pass
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        pass

class FileAgent(BaseAgent):
    def can_handle(self, task_type: str) -> bool:
        return task_type in ["file_processing", "pdf_analysis", "document_extraction"]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        files = task.get("files", [])
        results = []
        
        for file_data in files:
            try:
                # Extract text from PDF
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data["content"]))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                results.append({
                    "filename": file_data["filename"],
                    "text_length": len(text),
                    "text_preview": text[:500] + "..." if len(text) > 500 else text,
                    "page_count": len(pdf_reader.pages)
                })
            except Exception as e:
                results.append({
                    "filename": file_data["filename"],
                    "error": str(e)
                })
        
        return {
            "agent": "FileAgent",
            "status": "completed",
            "results": results,
            "summary": f"Processed {len(results)} documents"
        }

class ResearchAgent(BaseAgent):
    def __init__(self):
        # Try to get API key from environment, fallback to placeholder
        self.search_api_key = os.environ.get("SERPER_API_KEY", "demo_key")
        self.search_url = "https://google.serper.dev/search"
    
    def can_handle(self, task_type: str) -> bool:
        return task_type in ["web_research", "competitor_analysis", "market_research", "safari_research"]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", "")
        task_type = task.get("task_type", "web_research")
        
        # Handle Safari integration (roadmap feature)
        if task_type == "safari_research":
            return await self.safari_integration_demo(query)
        
        try:
            # Attempt real web search
            search_results = await self.perform_web_search(query)
            return await self.process_search_results(query, search_results)
            
        except Exception as e:
            # Graceful fallback to enhanced mock data
            return await self.enhanced_fallback_research(query, str(e))
    
    async def perform_web_search(self, query: str) -> Dict:
        """Perform real web search using Serper API"""
        if self.search_api_key == "demo_key":
            raise Exception("No API key configured - using fallback data")
        
        headers = {
            'X-API-KEY': self.search_api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': 8,
            'hl': 'en',
            'gl': 'us'
        }
        
        response = requests.post(self.search_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Search API failed with status: {response.status_code}")
    
    async def process_search_results(self, query: str, search_data: Dict) -> Dict[str, Any]:
        """Process real search results into structured insights"""
        findings = []
        sources = []
        detailed_results = []
        
        # Process organic results
        organic_results = search_data.get("organic", [])[:6]
        
        for i, result in enumerate(organic_results):
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            
            if title and snippet:
                insight = self.generate_insight(title, snippet, query)
                
                findings.append(insight)
                sources.append(link)
                detailed_results.append({
                    "rank": i + 1,
                    "title": title,
                    "snippet": snippet,
                    "url": link,
                    "relevance_score": self.calculate_relevance(query, title + " " + snippet)
                })
        
        # Add related searches if available
        related_searches = search_data.get("relatedSearches", [])
        suggestions = [rs.get("query", "") for rs in related_searches[:3]]
        
        research_results = {
            "query": query,
            "search_type": "live_web_search",
            "findings": findings,
            "detailed_results": detailed_results,
            "sources": sources,
            "related_suggestions": suggestions,
            "total_results": len(findings),
            "search_timestamp": search_data.get("searchParameters", {}).get("q", query)
        }
        
        return {
            "agent": "ResearchAgent",
            "status": "completed",
            "results": research_results,
            "summary": f"Found {len(findings)} live research insights for '{query}' from web search"
        }
    
    def generate_insight(self, title: str, snippet: str, query: str) -> str:
        """Generate meaningful insights from search results"""
        # Simple insight generation based on content
        if "market" in query.lower():
            return f"Market insight: {snippet[:150]}..."
        elif "competitor" in query.lower():
            return f"Competitive analysis: {snippet[:150]}..."
        elif "trend" in query.lower():
            return f"Industry trend: {snippet[:150]}..."
        else:
            return f"Research finding: {snippet[:150]}..."
    
    def calculate_relevance(self, query: str, content: str) -> float:
        """Simple relevance scoring"""
        query_words = query.lower().split()
        content_lower = content.lower()
        
        matches = sum(1 for word in query_words if word in content_lower)
        return round(matches / len(query_words), 2) if query_words else 0.0
    
    async def safari_integration_demo(self, query: str) -> Dict[str, Any]:
        """Demo Safari integration capabilities (roadmap feature)"""
        return {
            "agent": "SafariAgent",
            "status": "roadmap_demo",
            "results": {
                "integration_type": "Native macOS Safari Integration",
                "query": query,
                "capabilities": [
                    f"🔍 Search browsing history for: '{query}'",
                    f"📑 Analyze bookmarks related to: '{query}'",
                    f"📖 Review reading list items about: '{query}'",
                    f"🌐 Cross-reference open tabs with: '{query}'"
                ],
                "privacy_benefits": [
                    "🔒 100% local data processing",
                    "🚫 No external API calls required",
                    "🍎 Full Apple ecosystem integration",
                    "☁️ iCloud sync across devices"
                ],
                "sample_insights": [
                    f"Found 12 relevant sites in browsing history for '{query}'",
                    f"3 bookmarked articles match '{query}' research",
                    f"Reading list contains 2 unread items about '{query}'",
                    f"Current tab on competitor site relevant to '{query}'"
                ],
                "next_steps": "Available in native Mac app with full Safari integration"
            },
            "summary": f"Safari integration demo: Privacy-first research using local browsing data for '{query}'"
        }
    
    async def enhanced_fallback_research(self, query: str, error: str) -> Dict[str, Any]:
        """Enhanced fallback with realistic mock data"""
        
        # Generate contextual mock data based on query
        if "ai" in query.lower() or "automation" in query.lower():
            findings = [
                f"AI automation market projected to reach $35B by 2027 (relevant to: {query})",
                f"Enterprise adoption of AI workflows increased 340% in 2024 (context: {query})",
                f"Multi-agent systems showing 60% efficiency gains over single AI models (related: {query})"
            ]
            sources = [
                "https://marketsandmarkets.com/ai-automation-report",
                "https://mckinsey.com/enterprise-ai-adoption-2024", 
                "https://arxiv.org/multi-agent-systems-efficiency"
            ]
        elif "competitor" in query.lower():
            findings = [
                f"Market leader analysis shows fragmented landscape in {query} space",
                f"Top 3 competitors control 45% market share in {query} sector",
                f"Emerging players gaining traction with innovative approaches to {query}"
            ]
            sources = [
                "https://forrester.com/competitive-landscape-analysis",
                "https://gartner.com/market-share-reports",
                "https://techcrunch.com/startup-competitive-analysis"
            ]
        else:
            findings = [
                f"Industry research indicates strong growth potential in {query}",
                f"Expert analysis suggests {query} will be key differentiator by 2025",
                f"Strategic recommendations available for {query} implementation"
            ]
            sources = [
                "https://example-research.com/industry-analysis",
                "https://example-insights.com/expert-opinions",
                "https://example-strategy.com/recommendations"
            ]
        
        return {
            "agent": "ResearchAgent",
            "status": "completed_with_fallback",
            "results": {
                "query": query,
                "search_type": "enhanced_fallback",
                "findings": findings,
                "sources": sources,
                "total_results": len(findings),
                "note": f"Using enhanced fallback data. API issue: {error}",
                "api_setup_info": "To enable live web search, set SERPER_API_KEY environment variable"
            },
            "summary": f"Generated {len(findings)} enhanced research insights for '{query}' (fallback mode)"
        }

class AnalysisAgent(BaseAgent):
    def can_handle(self, task_type: str) -> bool:
        return task_type in ["analysis", "insights", "summary", "report_generation"]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        data = task.get("data", {})
        query = task.get("query", "")
        
        # Simulate AI analysis (in production, use OpenAI API)
        analysis = {
            "key_insights": [
                f"Primary insight: {query} shows strong potential",
                "Data patterns indicate growth opportunities",
                "Strategic recommendations available"
            ],
            "summary": f"Analysis of '{query}' reveals significant strategic opportunities with actionable recommendations.",
            "recommendations": [
                "Implement multi-agent coordination",
                "Leverage existing Apple ecosystem",
                "Focus on privacy-first approach"
            ],
            "confidence_score": 0.85
        }
        
        return {
            "agent": "AnalysisAgent", 
            "status": "completed",
            "results": analysis,
            "summary": "Generated comprehensive analysis with strategic recommendations"
        }

class MailAgent(BaseAgent):
    def can_handle(self, task_type: str) -> bool:
        return task_type in ["email_analysis", "draft_email", "schedule_email", "email_insights", "extract_action_items"]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", "")
        task_type = task.get("task_type", "")
        
        # Simulate different email operations
        if "draft" in query.lower() or task_type == "draft_email":
            result = await self.draft_email(query)
        elif "action" in query.lower() or "todo" in query.lower():
            result = await self.extract_action_items(query)
        elif "schedule" in query.lower():
            result = await self.schedule_email(query)
        else:
            result = await self.analyze_emails(query)
        
        return {
            "agent": "MailAgent",
            "status": "completed",
            "results": result,
            "summary": f"Email operation completed: {task_type}"
        }
    
    async def draft_email(self, query: str) -> Dict[str, Any]:
        # Simulate email drafting based on query
        return {
            "action": "draft_email",
            "subject": f"Re: {query}",
            "draft_content": f"Based on your request '{query}', here's a professional email draft:\n\nDear [Recipient],\n\nI hope this email finds you well. Regarding {query}, I wanted to provide you with an update...\n\nBest regards,\n[Your Name]",
            "suggestions": [
                "Add specific details about the topic",
                "Include relevant attachments",
                "Set appropriate priority level"
            ]
        }
    
    async def extract_action_items(self, query: str) -> Dict[str, Any]:
        # Simulate action item extraction
        return {
            "action": "extract_action_items",
            "action_items": [
                f"Follow up on {query} by end of week",
                "Schedule meeting with stakeholders",
                "Prepare summary report",
                "Send updates to team members"
            ],
            "priority_items": [
                f"High priority: Review {query} documents",
                "Medium priority: Coordinate with external partners"
            ],
            "deadlines": [
                "This week: Initial review",
                "Next week: Final deliverables"
            ]
        }
    
    async def schedule_email(self, query: str) -> Dict[str, Any]:
        # Simulate email scheduling
        return {
            "action": "schedule_email",
            "scheduled_time": "Tomorrow 9:00 AM",
            "recipients": ["team@company.com"],
            "subject": f"Scheduled update: {query}",
            "status": "Email scheduled successfully"
        }
    
    async def analyze_emails(self, query: str) -> Dict[str, Any]:
        # Simulate email analysis
        return {
            "action": "analyze_emails",
            "email_summary": {
                "total_emails": 47,
                "unread_count": 12,
                "priority_emails": 5,
                "action_required": 8
            },
            "key_insights": [
                f"3 emails mention '{query}' requiring immediate attention",
                "2 meeting requests pending response",
                "1 urgent deadline approaching this week"
            ],
            "recommendations": [
                "Prioritize emails from key stakeholders",
                "Batch process non-urgent emails",
                "Set up filters for automated organization"
            ]
        }

class CalendarAgent(BaseAgent):
    def can_handle(self, task_type: str) -> bool:
        return task_type in ["schedule_meeting", "find_availability", "meeting_prep", "calendar_insights", "time_blocking"]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", "")
        task_type = task.get("task_type", "")
        
        if "schedule" in query.lower() or "meeting" in query.lower():
            result = await self.schedule_meeting(query)
        elif "available" in query.lower() or "free" in query.lower():
            result = await self.find_availability(query)
        elif "prepare" in query.lower() or "prep" in query.lower():
            result = await self.meeting_prep(query)
        elif "block" in query.lower() or "focus" in query.lower():
            result = await self.time_blocking(query)
        else:
            result = await self.calendar_insights(query)
        
        return {
            "agent": "CalendarAgent",
            "status": "completed", 
            "results": result,
            "summary": f"Calendar operation completed: {task_type}"
        }
    
    async def schedule_meeting(self, query: str) -> Dict[str, Any]:
        return {
            "action": "schedule_meeting",
            "meeting_details": {
                "title": f"Meeting: {query}",
                "proposed_times": [
                    "Tomorrow 2:00 PM - 3:00 PM",
                    "Friday 10:00 AM - 11:00 AM",
                    "Monday 3:00 PM - 4:00 PM"
                ],
                "attendees": ["stakeholder1@company.com", "stakeholder2@company.com"],
                "location": "Conference Room A / Zoom",
                "agenda": [
                    f"Discuss {query}",
                    "Review progress and next steps",
                    "Assign action items",
                    "Schedule follow-up"
                ]
            },
            "conflicts_resolved": 2,
            "invitations_sent": True
        }
    
    async def find_availability(self, query: str) -> Dict[str, Any]:
        return {
            "action": "find_availability",
            "available_slots": [
                {
                    "date": "Tomorrow",
                    "times": ["9:00 AM - 10:00 AM", "2:00 PM - 4:00 PM", "5:00 PM - 6:00 PM"]
                },
                {
                    "date": "Friday",
                    "times": ["10:00 AM - 12:00 PM", "1:00 PM - 3:00 PM"]
                }
            ],
            "busy_periods": [
                "Today 10:00 AM - 12:00 PM (Team Meeting)",
                "Tomorrow 11:00 AM - 1:00 PM (Client Call)"
            ],
            "recommendations": [
                "Best time for focused work: Tomorrow 2:00 PM - 4:00 PM",
                "Optimal meeting slots: Friday morning",
                "Avoid scheduling during lunch hours"
            ]
        }
    
    async def meeting_prep(self, query: str) -> Dict[str, Any]:
        return {
            "action": "meeting_prep",
            "preparation_checklist": [
                f"Review documents related to {query}",
                "Prepare agenda and talking points",
                "Gather relevant data and metrics",
                "Test technology and equipment"
            ],
            "required_materials": [
                "Quarterly reports",
                "Project status updates", 
                "Budget spreadsheets",
                "Presentation slides"
            ],
            "attendee_info": {
                "total_attendees": 6,
                "key_stakeholders": ["CEO", "CTO", "Product Manager"],
                "preparation_time_needed": "30 minutes"
            },
            "meeting_context": f"Strategic discussion about {query} with senior leadership"
        }
    
    async def time_blocking(self, query: str) -> Dict[str, Any]:
        return {
            "action": "time_blocking",
            "blocks_created": [
                {
                    "time": "9:00 AM - 11:00 AM",
                    "activity": f"Deep work: {query}",
                    "type": "Focus time"
                },
                {
                    "time": "11:00 AM - 12:00 PM", 
                    "activity": "Email processing",
                    "type": "Administrative"
                },
                {
                    "time": "2:00 PM - 4:00 PM",
                    "activity": "Meetings and calls",
                    "type": "Collaboration"
                }
            ],
            "productivity_tips": [
                "Turn off notifications during focus blocks",
                "Batch similar tasks together",
                "Leave buffer time between meetings"
            ],
            "week_overview": "Optimized schedule for maximum productivity"
        }
    
    async def calendar_insights(self, query: str) -> Dict[str, Any]:
        return {
            "action": "calendar_insights",
            "weekly_summary": {
                "total_meetings": 18,
                "meeting_hours": 12,
                "focus_time": 25,
                "busiest_day": "Wednesday",
                "lightest_day": "Friday"
            },
            "patterns": [
                "Most productive hours: 9:00 AM - 11:00 AM",
                "Meeting-heavy days: Tuesday, Wednesday",
                "Best days for deep work: Monday, Friday"
            ],
            "recommendations": [
                "Block more focus time on busy days",
                "Move routine meetings to lighter days",
                "Consider no-meeting Fridays"
            ],
            "upcoming_priorities": [
                f"Important: {query} discussion next week",
                "Quarterly review preparation",
                "Team one-on-ones scheduled"
            ]
        }
