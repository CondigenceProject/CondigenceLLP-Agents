import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#6366f1"))
            self.drawString(54, 755, "CONDIGENCE LLP")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(140, 755, "|  AI Agentic Operations System — Technical & Non-Technical Architecture Guide")
            
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.75)
            self.line(54, 747, 558, 747)

        # Footer (all pages)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#94a3b8"))
        self.drawString(54, 35, "CONFIDENTIAL & PROPRIETARY — CONDIGENCE LLP")
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 35, page_str)
        
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.75)
        self.line(54, 45, 558, 45)
        
        self.restoreState()


def create_documentation_pdf(output_filename):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=48,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#1e1b4b")       # Dark indigo
    ACCENT = colors.HexColor("#4f46e5")        # Indigo accent
    ACCENT_LIGHT = colors.HexColor("#e0e7ff")  # Light indigo bg
    TEXT_DARK = colors.HexColor("#0f172a")     # Slate 900
    TEXT_MUTED = colors.HexColor("#475569")    # Slate 600
    BORDER_COLOR = colors.HexColor("#cbd5e1")  # Slate 300
    BG_CARD = colors.HexColor("#f8fafc")       # Slate 50

    # Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
        textColor=PRIMARY,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=ACCENT,
        spaceAfter=4
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=ACCENT,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_DARK,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_DARK,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11.5,
        textColor=TEXT_DARK
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=TEXT_DARK
    )

    story = []

    # ==================== COVER / HEADER BANNER ====================
    story.append(Paragraph("CONDIGENCE LLP", subtitle_style))
    story.append(Paragraph("AI Agentic Operations System", title_style))
    story.append(Paragraph("Comprehensive Technical & Non-Technical Architecture, Operations, Resilience & Monitoring Manual", ParagraphStyle('Sub', parent=body_style, fontSize=9, leading=12, textColor=TEXT_MUTED)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=6, spaceAfter=8))

    meta_table_data = [
        [
            Paragraph("<b>Version:</b> 1.0.0 (Production Blueprint)", table_cell_style),
            Paragraph("<b>Classification:</b> Enterprise Confidential", table_cell_style),
            Paragraph("<b>System Core:</b> LangGraph + FastAPI + React", table_cell_style)
        ],
        [
            Paragraph("<b>Author:</b> Condigence Engineering", table_cell_style),
            Paragraph("<b>Target Audience:</b> Business Owners & Developers", table_cell_style),
            Paragraph("<b>Status:</b> Active & Verified", table_cell_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[174, 174, 174])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # ==================== SECTION 1: NON-TECHNICAL OVERVIEW ====================
    story.append(Paragraph("1. Non-Technical Executive Overview", h1_style))
    story.append(Paragraph("The <b>Condigence AI Agentic Operations System</b> is an autonomous multi-agent operational platform designed to automate and orchestrate core enterprise workflows—including corporate compliance, financial drafting, client communications, HR operations, project tracking, and executive analytics—while enforcing <b>mandatory Human-in-the-Loop (HITL) authorization gates</b>.", body_style))

    # Callout Box: What it does
    callout_data = [[
        Paragraph("<b>Key Takeaway for Business Owners & Executives:</b><br/>"
                  "AI agents do not act uncontrollably. They research, calculate, structure, and prepare draft invoices, statutory filings, and emails. However, <i>no financial disbursement, client email, or legal document is released</i> without explicit human partner sign-off in the HITL Approval Queue.", callout_style)
    ]]
    callout_table = Table(callout_data, colWidths=[522])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ACCENT_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, ACCENT),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("How the Business Workflow Operates (Step-by-Step)", h2_style))
    story.append(Paragraph("• <b>Step 1: Strategic Instruction:</b> An executive submits an operational directive in plain language (e.g. <i>'Draft invoice for Acme Corp for INR 50,000 and notify them via email'</i>).", bullet_style))
    story.append(Paragraph("• <b>Step 2: AI CEO Strategic Planning:</b> The virtual CEO analyzes the instruction, breaks it down into required specialist tasks, and constructs a tactical execution plan.", bullet_style))
    story.append(Paragraph("• <b>Step 3: Autonomous Specialist Execution:</b> The AI Supervisor assigns worker agents in exact order (e.g. Finance Agent calculates taxes and prepares the invoice &rarr; Comms Agent crafts the client email).", bullet_style))
    story.append(Paragraph("• <b>Step 4: Quality & Safety Evaluation:</b> Automated safety evaluators verify calculation validity (e.g. ensuring positive amounts, correct GST rates, and standard statutory formats).", bullet_style))
    story.append(Paragraph("• <b>Step 5: Human Partner Authorization (HITL):</b> Generated artifacts appear in the Executive Portal with interactive previews. The partner clicks <i>Approve & Release</i> or <i>Reject</i>.", bullet_style))
    story.append(Paragraph("• <b>Step 6: Immutable Audit Trail:</b> Every single action, reasoning step, and partner approval is permanently recorded with cryptographic timestamps.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Business Benefits Matrix", h2_style))

    biz_table_data = [
        [Paragraph("Operational Pillar", table_header_style), Paragraph("Traditional Manual Workflow", table_header_style), Paragraph("Condigence Agentic System", table_header_style)],
        [
            Paragraph("<b>Finance & Billing</b>", table_cell_style),
            Paragraph("Manual Zoho entry, manual 18% GST calculation, risk of formula errors.", table_cell_style),
            Paragraph("Instant structured drafting, automated statutory GST engine, 1-click partner sign-off.", table_cell_style)
        ],
        [
            Paragraph("<b>MCA/ROC Compliance</b>", table_cell_style),
            Paragraph("Spreadsheet tracking, missed Form 8/Form 11 deadlines, penalty exposure.", table_cell_style),
            Paragraph("Autonomous regulatory monitoring, proactive statutory filing dossier generation.", table_cell_style)
        ],
        [
            Paragraph("<b>Client Comms</b>", table_cell_style),
            Paragraph("Delayed email drafting, inconsistent tone, scattered email threads.", table_cell_style),
            Paragraph("Context-aware professional drafts, omnichannel alignment (Gmail/WhatsApp).", table_cell_style)
        ],
        [
            Paragraph("<b>Payroll & HR</b>", table_cell_style),
            Paragraph("Manual leave reconciliation, complex TDS deduction math.", table_cell_style),
            Paragraph("Automated department breakdown, gross-to-net disbursement calculation.", table_cell_style)
        ]
    ]
    biz_table = Table(biz_table_data, colWidths=[110, 206, 206])
    biz_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(biz_table)

    story.append(PageBreak())

    # ==================== SECTION 2: TECHNICAL ARCHITECTURE ====================
    story.append(Paragraph("2. Technical Architecture & Component Specification", h1_style))
    story.append(Paragraph("The system implements a decoupled, high-concurrency client-server architecture powered by FastAPI and LangGraph with stateful event reduction.", body_style))

    story.append(Paragraph("Full Technology Stack Matrix", h2_style))

    tech_table_data = [
        [Paragraph("Layer", table_header_style), Paragraph("Technologies Used", table_header_style), Paragraph("Architectural Purpose & Responsibility", table_header_style)],
        [
            Paragraph("<b>Frontend Client</b>", table_cell_style),
            Paragraph("React 18, Vite 5, Lucide-React, CSS3 Design Tokens", table_cell_style),
            Paragraph("Executive Single Page Application (SPA), live directive dashboard, HITL queue, and visual trace inspector.", table_cell_style)
        ],
        [
            Paragraph("<b>API Gateway</b>", table_cell_style),
            Paragraph("FastAPI 0.110+, Uvicorn, Pydantic v2, WebSockets", table_cell_style),
            Paragraph("Asynchronous non-blocking REST gateway, lifespan connection managers, and WebSocket event emitters.", table_cell_style)
        ],
        [
            Paragraph("<b>Agent Orchestration</b>", table_cell_style),
            Paragraph("LangGraph 1.2+, LangChain Core, StateGraph", table_cell_style),
            Paragraph("Directed Acyclic Graph (DAG) state machine, multi-agent reducer state management, and supervisor routing.", table_cell_style)
        ],
        [
            Paragraph("<b>AI / LLM Layer</b>", table_cell_style),
            Paragraph("Groq (LLaMA-3.3 70B), Gemini 2.0, OpenAI GPT-4o", table_cell_style),
            Paragraph("Multi-tier LLM inference with ultra-fast execution, structured schema decoding, and fallback recovery.", table_cell_style)
        ],
        [
            Paragraph("<b>Persistence & Telemetry</b>", table_cell_style),
            Paragraph("MongoDB Atlas, Motor, Redis 8, Apache Kafka", table_cell_style),
            Paragraph("Immutable audit event streams, task state persistence, token bucket rate-limiting, and distributed caching.", table_cell_style)
        ]
    ]
    tech_table = Table(tech_table_data, colWidths=[100, 182, 240])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Specialized Multi-Agent Fleet Hierarchy", h2_style))
    story.append(Paragraph("The system partitions enterprise intelligence into 7 distinct roles:", body_style))

    agent_table_data = [
        [Paragraph("Agent Name", table_header_style), Paragraph("Role & Domain", table_header_style), Paragraph("Input Directive", table_header_style), Paragraph("Generated Output / Artifact", table_header_style)],
        [
            Paragraph("<b>AI_CEO</b>", table_cell_style),
            Paragraph("Strategic visionary & planner", table_cell_style),
            Paragraph("Executive strategic goal", table_cell_style),
            Paragraph("<code>strategic_plan</code>: Identified agents, decomposed sub-tasks, entities.", table_cell_style)
        ],
        [
            Paragraph("<b>FinanceAgent</b>", table_cell_style),
            Paragraph("Billing, GST, Zoho Books", table_cell_style),
            Paragraph("Billing directives", table_cell_style),
            Paragraph("<code>invoice_draft</code>: Base amount, 18% GST, invoice number, line items.", table_cell_style)
        ],
        [
            Paragraph("<b>CommsAgent</b>", table_cell_style),
            Paragraph("Gmail, WhatsApp, CRM", table_cell_style),
            Paragraph("Message/Notification requests", table_cell_style),
            Paragraph("<code>comms_draft</code>: Recipient, subject, contextual body copy.", table_cell_style)
        ],
        [
            Paragraph("<b>ComplianceAgent</b>", table_cell_style),
            Paragraph("MCA, ROC, LLP legalities", table_cell_style),
            Paragraph("Statutory filing requests", table_cell_style),
            Paragraph("<code>compliance_filing</code>: Form 8/11 checklist, authority deadlines.", table_cell_style)
        ],
        [
            Paragraph("<b>HRAgent</b>", table_cell_style),
            Paragraph("Payroll, Leaves, Onboarding", table_cell_style),
            Paragraph("Disbursement/HR goals", table_cell_style),
            Paragraph("<code>payroll_draft</code>: Gross disbursement, TDS, net pay, headcounts.", table_cell_style)
        ],
        [
            Paragraph("<b>ProjectAgent</b>", table_cell_style),
            Paragraph("Notion board synchronization", table_cell_style),
            Paragraph("Sprint/Milestone queries", table_cell_style),
            Paragraph("<code>project_status</code>: Active sprints, blocked milestones, highlights.", table_cell_style)
        ],
        [
            Paragraph("<b>AnalyticsAgent</b>", table_cell_style),
            Paragraph("P&L, Cash flow forecasting", table_cell_style),
            Paragraph("Financial metric requests", table_cell_style),
            Paragraph("<code>financial_report</code>: Gross revenue, OpEx, margin, cash health.", table_cell_style)
        ]
    ]
    agent_table = Table(agent_table_data, colWidths=[90, 114, 110, 208])
    agent_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(agent_table)

    story.append(PageBreak())

    # ==================== SECTION 3: LLM TIERS, ERROR HANDLING & MONITORING ====================
    story.append(Paragraph("3. LLM Orchestration, Fallback Strategy & Error Handling", h1_style))
    story.append(Paragraph("Enterprise reliability requires that transient LLM outages, API throttling, or malformed outputs never crash the application.", body_style))

    story.append(Paragraph("Multi-Tiered LLM Fallback Architecture", h2_style))
    story.append(Paragraph("The system implements a 4-tier graceful degradation strategy in <code>app/core/llm.py</code>:", body_style))
    story.append(Paragraph("• <b>Tier 1 (High-Performance Primary):</b> <code>Groq LLaMA-3.3-70B-Versatile</code> (sub-second latency, structured extraction).", bullet_style))
    story.append(Paragraph("• <b>Tier 2 (High-Context Secondary):</b> <code>Google Gemini 2.0 Flash</code> via OpenAI compatibility layer.", bullet_style))
    story.append(Paragraph("• <b>Tier 3 (Enterprise Tertiary):</b> <code>OpenAI GPT-4o / GPT-4o-mini</code>.", bullet_style))
    story.append(Paragraph("• <b>Tier 4 (Deterministic Heuristic Fallback):</b> Safe rule-based algorithmic drafting ensuring 100% uptime even during complete cloud outages.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Detailed Error Handling Architecture", h2_style))

    error_table_data = [
        [Paragraph("Failure Vector", table_header_style), Paragraph("Root Cause / Scenario", table_header_style), Paragraph("Automated Mitigation & Recovery Mechanism", table_header_style)],
        [
            Paragraph("<b>LLM Markdown & Token Contamination</b>", table_cell_style),
            Paragraph("Reasoning models outputting <code>&lt;think&gt;</code> tags or conversational text before JSON.", table_cell_style),
            Paragraph("<code>extract_json_from_llm()</code> strips reasoning tags via RegEx, inspects code fences, and uses outermost bracket matching.", table_cell_style)
        ],
        [
            Paragraph("<b>Worker Route Deadlock</b>", table_cell_style),
            Paragraph("Worker finishes but CEO had planned multiple downstream agents.", table_cell_style),
            Paragraph("<code>route_from_worker()</code> dynamically compares <code>strategic_plan</code> against <code>completed_steps</code> and auto-chains next agent.", table_cell_style)
        ],
        [
            Paragraph("<b>Safety Rule Violation</b>", table_cell_style),
            Paragraph("Worker outputs negative invoice total or truncated email body.", table_cell_style),
            Paragraph("<code>SupervisorEvaluator.validate_step()</code> inspects math and payload integrity before registering for HITL review.", table_cell_style)
        ],
        [
            Paragraph("<b>Backend Network Disconnection</b>", table_cell_style),
            Paragraph("FastAPI process stopped or dev proxy connection refused.", table_cell_style),
            Paragraph("React UI displays real-time <code>Backend Offline</code> banner with 1-click Reconnect and surfaces exact HTTP status codes.", table_cell_style)
        ]
    ]
    error_table = Table(error_table_data, colWidths=[120, 162, 240])
    error_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(error_table)

    story.append(PageBreak())

    # ==================== SECTION 4 & 5: OBSERVABILITY & ROADMAP ====================
    story.append(Paragraph("4. Output Monitoring, Observability & Auditing", h1_style))
    story.append(Paragraph("Output verification occurs at three synchronized layers:", body_style))

    story.append(Paragraph("• <b>Layer 1 — Automated Supervisor Evaluation:</b> Every worker artifact passes through <code>SupervisorEvaluator</code> to ensure domain constraints (positive totals, valid tax rates, mandatory disclaimer copy).", bullet_style))
    story.append(Paragraph("• <b>Layer 2 — Immutable Audit Logging (AuditService):</b> Every action is logged with actor type (<code>HUMAN</code> / <code>AGENT</code>), exact payload, timestamp, and status. Audit events are streamed to Apache Kafka (<code>condigence.audit.events</code>) and stored in MongoDB Atlas.", bullet_style))
    story.append(Paragraph("• <b>Layer 3 — Real-Time Executive Trace Inspector:</b> The web portal provides live step-by-step visual execution flow, artifact rendering cards, and raw JSON payload inspection.", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("5. Future Upgrade & Extension Roadmap", h1_style))
    story.append(Paragraph("• <b>1. Live External API Integrations:</b> Connect Zoho Books OAuth2 for direct invoice push, Gmail API / WhatsApp Cloud API for client dispatch, and Notion API for two-way task sync upon human approval.", bullet_style))
    story.append(Paragraph("• <b>2. Database Persistence Migration:</b> Transition in-memory task dictionary to distributed MongoDB collections with automated indexing.", bullet_style))
    story.append(Paragraph("• <b>3. Role-Based Access Control (RBAC):</b> Introduce granular partner authorization (e.g. Partner A signs financial invoices > INR 1,00,000; Partner B signs MCA filings).", bullet_style))
    story.append(Paragraph("• <b>4. Voice Directive Input:</b> Integrate Whisper speech-to-text for hands-free executive directive dispatching.", bullet_style))
    story.append(Paragraph("• <b>5. Vector Memory & RAG Knowledgebase:</b> Connect Pinecone/Qdrant vector stores with LLP historical agreements and past MCA resolutions.", bullet_style))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Documentation successfully created at: {output_filename}")

if __name__ == "__main__":
    output_path = os.path.join(os.getcwd(), "Condigence_System_Architecture_and_Operations_Manual.pdf")
    create_documentation_pdf(output_path)
