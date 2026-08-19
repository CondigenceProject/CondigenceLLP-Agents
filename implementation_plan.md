# Condigence LLP: AI Agentic Operations System - Technical Project Structure & Architecture

## System Overview
Condigence LLP requires an enterprise-grade, Human-in-the-Loop (HITL) Multi-Agent Operations System. The system features a **Dual-Tier Management Model** (AI CEO strategic reasoning + LangGraph AI Supervisor execution) that coordinates six specialized worker agents (Comms, Finance, Compliance, Project, HR, Analytics) while ensuring that no financial movements, client emails, or legal filings occur without human approval.

---

## Proposed Technical Project Structure

```text
Condigence/
├── .env.example                       # Template for API keys (OpenAI, LangSmith, Zoho, Mongo, Redis, etc.)
├── requirements.txt                   # Production Python dependencies
├── Dockerfile                         # Container build for FastAPI backend
├── docker-compose.yml                 # Local dev orchestration (FastAPI, Redis, Mongo, n8n)
├── main.py                            # Application entry point (Uvicorn runner)
│
├── app/
│   ├── __init__.py
│   ├── config.py                      # Pydantic BaseSettings for strongly-typed env config
│   ├── server.py                      # FastAPI application factory, middleware, exception handlers
│   │
│   ├── core/                          # Core infrastructure & system utilities
│   │   ├── __init__.py
│   │   ├── db.py                      # Async MongoDB client (Motor) connection lifecycle
│   │   ├── redis_client.py            # Redis client (caching, distributed locks, rate limits)
│   │   ├── security.py                # JWT creation/verification, password hashing, RBAC
│   │   └── audit.py                   # Immutable event logger for all agent & human actions
│   │
│   ├── models/                        # Pydantic schemas & MongoDB document models
│   │   ├── __init__.py
│   │   ├── user.py                    # User identities & roles (Owner, Ops Manager, Accounts Assistant)
│   │   ├── task.py                    # Agent task lifecycle & state tracking
│   │   ├── approval.py                # Approval Queue tickets (Draft Invoice, Outgoing Email, Filings)
│   │   └── audit_log.py               # Audit trail records (Actor, Agent, Tool, In/Out payload)
│   │
│   ├── agents/                        # Multi-Agent Core (LangGraph & LangChain)
│   │   ├── __init__.py
│   │   ├── state.py                   # Central AgentState TypedDict definition
│   │   ├── ceo/                       # Tier 1: AI CEO (Strategic Planning)
│   │   │   ├── __init__.py
│   │   │   ├── agent.py               # AI CEO prompt, goal decomposition & review logic
│   │   │   └── router.py              # Bridges human executive directives to the Supervisor
│   │   ├── supervisor/                # Tier 2: AI Supervisor (LangGraph StateGraph Orchestrator)
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py        # LangGraph StateGraph builder, routing node & edges
│   │   │   └── evaluator.py           # Worker output validation & replanning logic
│   │   └── workers/                   # Specialized Domain Worker Agents
│   │       ├── __init__.py
│   │       ├── base.py                # Base worker class with automatic tool-level audit logging
│   │       ├── comms_agent.py         # Drafts emails/WhatsApp, qualifies leads, updates CRM
│   │       ├── finance_agent.py       # Drafts Zoho invoices, calculates GST, tags expenses
│   │       ├── compliance_agent.py    # Monitors MCA/ROC statutory dates & checklists
│   │       ├── project_agent.py       # Notion task sync & milestone tracking
│   │       ├── hr_agent.py            # Leave balances, onboarding checklists, payroll drafting
│   │       └── analytics_agent.py     # Revenue reports, monthly P&L drafts, metrics
│   │
│   ├── integrations/                  # External service adapters & tool wrappers
│   │   ├── __init__.py
│   │   ├── zoho/                      # Zoho Books & Zoho CRM OAuth2 & REST clients
│   │   │   ├── __init__.py
│   │   │   ├── books_client.py
│   │   │   └── crm_client.py
│   │   ├── notion/                    # Notion API client for tasks & SOPs
│   │   │   ├── __init__.py
│   │   │   └── notion_client.py
│   │   ├── communication/             # Email & Messaging adapters
│   │   │   ├── __init__.py
│   │   │   ├── gmail_client.py
│   │   │   └── whatsapp_client.py
│   │   └── vector_store/              # Pinecone / Vector RAG client for SOP retrieval
│   │       ├── __init__.py
│   │       └── pinecone_client.py
│   │
│   ├── api/                           # FastAPI REST and WebSocket Endpoints
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py              # Main V1 API router aggregation
│   │   │   ├── auth.py                # Authentication & user profile endpoints
│   │   │   ├── agents.py              # Agent task trigger & execution status endpoints
│   │   │   ├── approvals.py           # HITL Approval queue (List, Approve, Reject, Edit)
│   │   │   ├── audit.py               # Audit trail query endpoints with filtering
│   │   │   └── webhooks.py            # Webhook receivers (Gmail, WhatsApp, n8n triggers)
│   │   └── websockets/
│   │       ├── __init__.py
│   │       └── stream.py              # Real-time WebSocket streaming of agent reasoning & steps
│   │
│   └── workflows/                     # Automated event flows & cron bridges
│       ├── __init__.py
│       └── n8n_bridge.py              # n8n trigger webhooks and scheduled sync handlers
```

---

## Technical Flow & Execution Strategy

1. **State Machine (LangGraph)**:
   * State schema (`AgentState`) maintains conversation history, active agent, pending sub-tasks, generated artifacts (invoices, emails, memos), and approval requirements.
   * `Supervisor` node evaluates the task state after every worker step. If human review is necessary, an approval ticket is created in MongoDB and execution is paused until human resolution.

2. **Strict Human-in-the-Loop (HITL) Enforcement**:
   * Financial transactions (Zoho invoices/payments), client-facing messages (Gmail/WhatsApp), and legal filings (MCA/ROC) create immutable records in `approvals` collection with status `PENDING`.
   * Only authenticated human managers (Owner, Ops Manager, Accounts Assistant) can trigger `/api/v1/approvals/{id}/approve` to release the action.

3. **Audit Trail**:
   * Every LLM call, tool invocation, and human decision writes directly to an immutable `audit_logs` collection in MongoDB storing: timestamp, actor (agent or user ID), action name, input payload, and output response.

---

## User Review Required

> [!IMPORTANT]
> **Key Architectural Decisions for Confirmation**:
> 1. **Framework Confirmation**: LangGraph is the primary orchestration framework with FastAPI as the backend API.
> 2. **Phased Build-Out**: We will build the foundational core (FastAPI + Config + DB/Redis + LangGraph Orchestration Skeleton + Mock Integrations + Approval API) in Step 1, followed by live third-party connectors (Zoho, Notion, Gmail, WhatsApp).

---

## Step 1 Action Plan (To Execute Upon Approval)

1. **Initialize Dependencies & Config**: Create `requirements.txt`, `.env.example`, and `app/config.py`.
2. **Build Core & Database**: Implement async MongoDB (Motor) connection in `app/core/db.py`, Redis client in `app/core/redis_client.py`, and audit logging service in `app/core/audit.py`.
3. **Implement Models**: Create Pydantic/Mongo models for `User`, `Task`, `Approval`, and `AuditLog`.
4. **Scaffold LangGraph Agent Engine**: Build `AgentState`, AI CEO prompt router, AI Supervisor controller, and worker agent node templates with tool auditing.
5. **Implement FastAPI API Routes**: Create `/api/v1/agents/run`, `/api/v1/approvals`, and healthcheck endpoints in `app/server.py` and `main.py`.
6. **Verify End-to-End**: Run a simulated execution test showing the AI CEO receiving a goal, the Supervisor delegating to Comms/Finance, generating an approval ticket, and logging to the audit collection.

---

## Verification Plan

### Automated & Functional Tests
* Validate FastAPI server boots up cleanly on `http://127.0.0.1:8000`.
* Test `/health` and `/api/v1/agents/run` endpoints using Python test scripts.
* Verify LangGraph state transitions and HITL staging without uncaught exceptions.
