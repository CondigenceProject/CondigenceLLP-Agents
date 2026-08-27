import json
import logging
import uuid
from typing import Any, Dict
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.agents.workers.base import BaseWorkerAgent
from app.core.llm import get_llm

logger = logging.getLogger("condigence.workers.comms")

COMMS_SYSTEM_PROMPT = """You are the Communications Specialist Agent (CommsAgent) of Condigence LLP.
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
            description="Manages business communications across Gmail, WhatsApp, and CRM lead interactions."
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        goal = state.get("goal", "")
        artifacts = state.get("artifacts", {})
        
        logger.info(f"CommsAgent processing task related to: '{goal}'")
        
        draft_subject = "Update from Condigence LLP"
        draft_recipient = "client@example.com"
        draft_body = (
            f"Dear Client,\n\n"
            f"Regarding your request: {goal}\n"
            f"We have prepared the necessary details and will assist you with the next steps.\n\n"
            f"Best regards,\nCondigence LLP Operations Team"
        )
        channel = "EMAIL"

        # Try to generate using live LLM
        try:
            llm = get_llm(temperature=0.3)
            if llm:
                prompt_text = f"Executive Directive: {goal}\nExisting Context & Artifacts: {json.dumps(artifacts)}"
                resp = await llm.ainvoke([
                    SystemMessage(content=COMMS_SYSTEM_PROMPT),
                    HumanMessage(content=prompt_text)
                ])
                content = resp.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                parsed = json.loads(content)
                draft_subject = parsed.get("subject", draft_subject)
                draft_recipient = parsed.get("recipient", draft_recipient)
                draft_body = parsed.get("body", draft_body)
                channel = parsed.get("channel", "EMAIL")
        except Exception as e:
            logger.warning(f"CommsAgent LLM fallback: {e}")

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

