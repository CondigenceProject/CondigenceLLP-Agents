import json
import logging
import re
import uuid
from typing import Any, Dict, List
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.agents.workers.base import BaseWorkerAgent
from app.core.llm import get_llm
from app.core.json_util import extract_json_from_llm

logger = logging.getLogger("condigence.workers.comms")

COMMS_MVP_SYSTEM_PROMPT = """You are the Principal Product Architect & Communications Specialist of Condigence LLP.
Your job is to analyze raw client requirements, synthesize an executable Phase 1 MVP (Minimum Viable Product) specification, and draft a high-impact, professional client proposal email.

Instructions:
1. Extract or infer:
   - "client_name": e.g. "Nexus Retail"
   - "contact_email": client's email address (e.g. "rishav.condigence@gmail.com") or default "client@example.com"
   - "project_name": concise title (e.g. "AI WhatsApp Order & Support Assistant")
   - "timeline_weeks": realistic delivery timeline in weeks (e.g. 3)
2. Define "p0_features": 3 to 5 core Must-Have modules required to launch the MVP successfully. Each item must have:
   - "feature": module name
   - "description": specific deliverable
   - "effort_days": estimated engineering days (integer, e.g. 4)
3. Define "out_of_scope": 2 to 4 items explicitly deferred to Phase 2 to prevent scope creep.
4. Define "tech_stack": list of 3-5 recommended technologies.
5. Define "clarifying_questions": 2-3 targeted technical or business questions for the client.
6. Draft "draft_email":
   - "recipient": client's email
   - "subject": "MVP Scope & Project Proposal: [Project Name] – Condigence LLP"
   - "body": Professional, executive-ready proposal covering the objectives, MVP scope highlights, timeline, clarifying questions, and next steps for kickoff.

Respond ONLY with valid JSON:
{
  "client_name": "Nexus Retail",
  "contact_email": "rishav.condigence@gmail.com",
  "project_name": "AI WhatsApp Customer Support Bot",
  "timeline_weeks": 3,
  "summary": "Rapid 3-week MVP to deploy an AI-powered WhatsApp bot for order status, Notion inventory sync, and sentiment-based human escalation.",
  "p0_features": [
    {"feature": "WhatsApp Cloud Webhook & Intent Engine", "description": "Integrates Meta WhatsApp Cloud API for conversational intake and natural language order queries.", "effort_days": 5},
    {"feature": "Notion Inventory Real-time Sync", "description": "Two-way integration with Notion database to query product availability and order records.", "effort_days": 4},
    {"feature": "Sentiment-based Escalation Alerting", "description": "Monitors customer sentiment; triggers immediate alert to human support team if frustration is detected.", "effort_days": 3},
    {"feature": "End-to-End QA, Testing & Deployment", "description": "Comprehensive integration testing, exception handling, and staging sign-off.", "effort_days": 3}
  ],
  "out_of_scope": [
    "Voice note transcription and multi-lingual voice calls (Phase 2)",
    "Direct payment gateway settlement inside WhatsApp chat (Phase 2)",
    "Legacy ERP custom schema migrations"
  ],
  "tech_stack": ["FastAPI", "Meta WhatsApp Cloud API", "Notion API", "LangGraph", "Redis"],
  "clarifying_questions": [
    "Do you already have a Meta Business Manager verified account for WhatsApp Cloud API, or should we assist with provisioning?",
    "Could you share a sample Notion inventory schema or database structure?"
  ],
  "draft_email": {
    "recipient": "rishav.condigence@gmail.com",
    "subject": "MVP Scope & Project Proposal: AI WhatsApp Customer Support Bot – Condigence LLP",
    "body": "Dear [Client],\n\nThank you for reaching out..."
  }
}
"""

COMMS_GENERAL_SYSTEM_PROMPT = """You are the Communications Specialist Agent (CommsAgent) of Condigence LLP.
Your job is to draft professional, context-rich client emails, WhatsApp messages, or business communications based on executive instructions and company context.

Respond in valid JSON:
{
  "subject": "Clear, professional email subject",
  "recipient": "client@example.com or extracted contact",
  "body": "Complete, polite, professional email or message body tailored to the exact directive.",
  "channel": "EMAIL"
}
"""


class CommsAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(
            name="CommsAgent",
            description="Manages business communications, client MVP proposal formulation, and lead onboarding."
        )

    def _extract_email(self, text: str) -> str:
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return emails[0] if emails else "client@example.com"

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        goal = state.get("goal", "")
        artifacts = state.get("artifacts", {})
        
        logger.info(f"CommsAgent processing task related to: '{goal}'")
        
        goal_lower = goal.lower()
        is_mvp_task = any(k in goal_lower for k in [
            "raw requirement", "client:", "client requirement", "mvp", "quotation", "scope",
            "bot", "app", "feature", "notion inventory", "whatsapp customer support"
        ])

        if is_mvp_task:
            return await self._handle_mvp_scoping(goal, artifacts)
        else:
            return await self._handle_general_communication(goal, artifacts)

    async def _handle_mvp_scoping(self, goal: str, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        extracted_email = self._extract_email(goal)
        
        # Default fallback structure if LLM is offline
        mvp_data = {
            "client_name": "Valued Client",
            "contact_email": extracted_email,
            "project_name": "AI Solution MVP",
            "timeline_weeks": 3,
            "summary": f"Executive Phase 1 MVP Scope based on requirements: {goal[:120]}...",
            "p0_features": [
                {"feature": "Core AI Logic & Intent Engine", "description": "Natural language processing of incoming client requests.", "effort_days": 5},
                {"feature": "External System Integration", "description": "Two-way API connector for live data sync.", "effort_days": 4},
                {"feature": "Notification & Escalation Layer", "description": "Automated human alert system for critical inquiries.", "effort_days": 3},
                {"feature": "Staging QA & Production Rollout", "description": "Verification, security review, and cloud deployment.", "effort_days": 3}
            ],
            "out_of_scope": [
                "Advanced multi-language voice transcription (Deferred to Phase 2)",
                "Custom legacy CRM deep-syncing (Deferred to Phase 2)"
            ],
            "tech_stack": ["FastAPI", "LangGraph", "Python 3.11", "Redis", "Cloud Webhooks"],
            "clarifying_questions": [
                "What is your preferred cloud deployment environment (GCP, AWS, or local host)?",
                "Are there any specific rate limits or security policies we should conform to?"
            ],
            "draft_email": {
                "recipient": extracted_email,
                "subject": "MVP Scope & Project Proposal – Condigence LLP",
                "body": (
                    f"Dear Client,\n\n"
                    f"Thank you for sharing your project requirements with Condigence LLP.\n\n"
                    f"We have structured an agile Phase 1 MVP designed to achieve rapid delivery within 3 weeks.\n\n"
                    f"Key Deliverables:\n"
                    f"- WhatsApp & Natural Language Automation\n"
                    f"- Live Inventory Sync & Data Pipeline\n"
                    f"- Intelligent Escalation to Human Support\n\n"
                    f"Please review this proposal and let us know if you have any questions.\n\n"
                    f"Best regards,\nCondigence LLP Operations Team"
                )
            }
        }

        # Try to refine with LLM
        try:
            llm = get_llm(temperature=0.2)
            if llm:
                prompt_text = f"Client Requirement Directive: {goal}\nExisting Context: {json.dumps(artifacts)}"
                resp = await llm.ainvoke([
                    SystemMessage(content=COMMS_MVP_SYSTEM_PROMPT),
                    HumanMessage(content=prompt_text)
                ])
                parsed = extract_json_from_llm(resp.content)
                if parsed and isinstance(parsed, dict):
                    mvp_data.update(parsed)
                    if "contact_email" not in parsed or parsed["contact_email"] == "client@example.com":
                        mvp_data["contact_email"] = extracted_email
                    if "draft_email" in parsed and isinstance(parsed["draft_email"], dict):
                        parsed["draft_email"]["recipient"] = extracted_email
        except Exception as e:
            logger.warning(f"CommsAgent LLM MVP fallback: {e}")

        approval_id = str(uuid.uuid4())[:8]
        draft_email = mvp_data.get("draft_email", {})

        step_record = await self.log_action(
            action="FORMULATE_MVP_PROPOSAL",
            input_data={"goal": goal},
            output_data={"mvp_proposal": mvp_data, "requires_approval": True}
        )

        return {
            "completed_steps": [step_record],
            "artifacts": {
                "mvp_proposal": mvp_data,
                "comms_draft": draft_email
            },
            "requires_approval": True,
            "pending_approval_id": approval_id,
            "approval_type": "MVP_PROPOSAL",
            "approval_payload": mvp_data,
            "current_agent": "AI_Supervisor",
            "next_step": None,
            "status": "AWAITING_APPROVAL",
            "summary": f"Phase 1 MVP Scope & Proposal drafted for {mvp_data.get('client_name')} ({mvp_data.get('project_name')}). Awaiting human approval."
        }

    async def _handle_general_communication(self, goal: str, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        draft_subject = "Update from Condigence LLP"
        draft_recipient = self._extract_email(goal)
        draft_body = (
            f"Dear Client,\n\n"
            f"Regarding your request: {goal}\n"
            f"We have prepared the necessary details and will assist you with the next steps.\n\n"
            f"Best regards,\nCondigence LLP Operations Team"
        )
        channel = "EMAIL"

        try:
            llm = get_llm(temperature=0.3)
            if llm:
                prompt_text = f"Executive Directive: {goal}\nExisting Context & Artifacts: {json.dumps(artifacts)}"
                resp = await llm.ainvoke([
                    SystemMessage(content=COMMS_GENERAL_SYSTEM_PROMPT),
                    HumanMessage(content=prompt_text)
                ])
                parsed = extract_json_from_llm(resp.content)
                if parsed:
                    draft_subject = parsed.get("subject", draft_subject)
                    draft_recipient = parsed.get("recipient", draft_recipient)
                    draft_body = parsed.get("body", draft_body)
                    channel = parsed.get("channel", "EMAIL")
        except Exception as e:
            logger.warning(f"CommsAgent LLM general fallback: {e}")

        approval_id = str(uuid.uuid4())[:8]
        approval_payload = {
            "channel": channel,
            "recipient": draft_recipient,
            "subject": draft_subject,
            "body": draft_body,
        }

        step_record = await self.log_action(
            action="DRAFT_COMMUNICATION",
            input_data={"goal": goal, "context": artifacts},
            output_data={"draft_email": approval_payload, "requires_approval": True}
        )

        return {
            "completed_steps": [step_record],
            "artifacts": {"comms_draft": approval_payload},
            "requires_approval": True,
            "pending_approval_id": approval_id,
            "approval_type": "CLIENT_EMAIL",
            "approval_payload": approval_payload,
            "current_agent": "AI_Supervisor",
            "next_step": None,
            "status": "AWAITING_APPROVAL",
            "summary": f"Communication drafted: '{draft_subject}' (Approval ID: {approval_id})"
        }


comms_agent = CommsAgent()
