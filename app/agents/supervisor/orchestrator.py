import logging
from typing import Any, Dict
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.ceo.agent import ai_ceo
from app.agents.workers.comms_agent import comms_agent
from app.agents.workers.finance_agent import finance_agent
from app.agents.workers.compliance_agent import compliance_agent
from app.agents.workers.project_agent import project_agent
from app.agents.workers.hr_agent import hr_agent
from app.agents.workers.analytics_agent import analytics_agent
from app.agents.supervisor.evaluator import evaluator

logger = logging.getLogger("condigence.supervisor.orchestrator")


# Node Callables
async def ceo_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Executing StateGraph Node: CEO")
    return await ai_ceo.analyze_and_plan(state)


async def finance_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Executing StateGraph Node: FinanceAgent")
    res = await finance_agent.execute(state)
    evaluator.validate_step(state, res)
    return res


async def comms_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Executing StateGraph Node: CommsAgent")
    res = await comms_agent.execute(state)
    evaluator.validate_step(state, res)
    return res


async def compliance_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Executing StateGraph Node: ComplianceAgent")
    res = await compliance_agent.execute(state)
    evaluator.validate_step(state, res)
    return res


async def project_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Executing StateGraph Node: ProjectAgent")
    return await project_agent.execute(state)


async def hr_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Executing StateGraph Node: HRAgent")
    return await hr_agent.execute(state)


async def analytics_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Executing StateGraph Node: AnalyticsAgent")
    return await analytics_agent.execute(state)


# Supervisor Routing Logic
def route_from_ceo(state: AgentState) -> str:
    next_step = state.get("next_step")
    if next_step in ["FinanceAgent", "CommsAgent", "ComplianceAgent", "ProjectAgent", "HRAgent", "AnalyticsAgent"]:
        return next_step
    return END


def route_from_worker(state: AgentState) -> str:
    next_step = state.get("next_step")
    if next_step and next_step in ["CommsAgent", "FinanceAgent", "ComplianceAgent", "ProjectAgent", "HRAgent", "AnalyticsAgent"]:
        return next_step
    return END


def build_orchestrator_graph():
    """
    Assembles the LangGraph StateGraph connecting CEO -> Supervisor -> Specialized Workers.
    """
    workflow = StateGraph(AgentState)

    # Register Nodes
    workflow.add_node("AI_CEO", ceo_node)
    workflow.add_node("FinanceAgent", finance_node)
    workflow.add_node("CommsAgent", comms_node)
    workflow.add_node("ComplianceAgent", compliance_node)
    workflow.add_node("ProjectAgent", project_node)
    workflow.add_node("HRAgent", hr_node)
    workflow.add_node("AnalyticsAgent", analytics_node)

    # Entrypoint
    workflow.set_entry_point("AI_CEO")

    # Conditional Routing from CEO
    workflow.add_conditional_edges(
        "AI_CEO",
        route_from_ceo,
        {
            "FinanceAgent": "FinanceAgent",
            "CommsAgent": "CommsAgent",
            "ComplianceAgent": "ComplianceAgent",
            "ProjectAgent": "ProjectAgent",
            "HRAgent": "HRAgent",
            "AnalyticsAgent": "AnalyticsAgent",
            END: END
        }
    )

    # Conditional Routing from Workers (Supervisor Handoff)
    for worker in ["FinanceAgent", "CommsAgent", "ComplianceAgent", "ProjectAgent", "HRAgent", "AnalyticsAgent"]:
        workflow.add_conditional_edges(
            worker,
            route_from_worker,
            {
                "CommsAgent": "CommsAgent",
                "FinanceAgent": "FinanceAgent",
                "ComplianceAgent": "ComplianceAgent",
                "ProjectAgent": "ProjectAgent",
                "HRAgent": "HRAgent",
                "AnalyticsAgent": "AnalyticsAgent",
                END: END
            }
        )

    return workflow.compile()


agent_orchestrator = build_orchestrator_graph()
