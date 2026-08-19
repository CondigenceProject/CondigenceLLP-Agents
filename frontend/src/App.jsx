import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  CheckCircle2,
  AlertCircle,
  Clock,
  Send,
  FileText,
  DollarSign,
  Mail,
  ShieldCheck,
  FolderKanban,
  Users,
  BarChart3,
  RefreshCw,
  Eye,
  Check,
  X,
  Sparkles,
  ArrowRight,
  Database,
  Cpu,
  Layers
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [health, setHealth] = useState(null);
  const [approvals, setApprovals] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState('');

  // Command Center Goal execution state
  const [goalInput, setGoalInput] = useState('');
  const [runningTask, setRunningTask] = useState(null);
  const [taskInProgress, setTaskInProgress] = useState(false);

  // Fetch initial data
  const fetchData = async () => {
    try {
      // 1. Health
      const hRes = await fetch('/health');
      if (hRes.ok) setHealth(await hRes.json());

      // 2. Approvals
      const appRes = await fetch('/api/v1/approvals');
      if (appRes.ok) setApprovals(await appRes.json());

      // 3. Audit Logs
      const aRes = await fetch('/api/v1/audit/logs?limit=25');
      if (aRes.ok) setAuditLogs(await aRes.json());
    } catch (e) {
      console.error('Error fetching dashboard data:', e);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, []);

  // Handle Goal Launch
  const handleLaunchGoal = async (e) => {
    e.preventDefault();
    if (!goalInput.trim()) return;

    setTaskInProgress(true);
    setRunningTask(null);
    setActionMsg('');

    try {
      const res = await fetch('/api/v1/agents/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal: goalInput,
          requester_role: 'OWNER',
          context: {}
        })
      });
      if (res.ok) {
        const data = await res.json();
        setRunningTask(data);
        setGoalInput('');
        fetchData();
      }
    } catch (err) {
      console.error('Task launch failed:', err);
    } finally {
      setTaskInProgress(false);
    }
  };

  // Handle Approval Action
  const handleApprovalAction = async (ticketId, action) => {
    try {
      const res = await fetch(`/api/v1/approvals/${ticketId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: action,
          notes: `Actioned via Owner Portal by Vishal Aryan`
        })
      });
      if (res.ok) {
        setActionMsg(`Ticket ${ticketId} was successfully ${action.toLowerCase()}d.`);
        fetchData();
        setTimeout(() => setActionMsg(''), 4000);
      }
    } catch (err) {
      console.error('Approval action error:', err);
    }
  };

  const pendingCount = approvals.filter(a => a.status === 'PENDING').length;

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Layers size={22} />
          </div>
          <div className="brand-text">
            <h1>Condigence</h1>
            <span>AI Operations</span>
          </div>
        </div>

        <nav className="nav-menu">
          <button
            className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <div className="nav-item-content">
              <LayoutDashboard size={18} />
              <span>Overview</span>
            </div>
          </button>

          <button
            className={`nav-item ${activeTab === 'approvals' ? 'active' : ''}`}
            onClick={() => setActiveTab('approvals')}
          >
            <div className="nav-item-content">
              <ShieldCheck size={18} />
              <span>HITL Approvals</span>
            </div>
            {pendingCount > 0 && <span className="nav-badge">{pendingCount}</span>}
          </button>

          <button
            className={`nav-item ${activeTab === 'command' ? 'active' : ''}`}
            onClick={() => setActiveTab('command')}
          >
            <div className="nav-item-content">
              <Sparkles size={18} />
              <span>AI Command</span>
            </div>
          </button>

          <button
            className={`nav-item ${activeTab === 'fleet' ? 'active' : ''}`}
            onClick={() => setActiveTab('fleet')}
          >
            <div className="nav-item-content">
              <Cpu size={18} />
              <span>Agent Fleet</span>
            </div>
          </button>

          <button
            className={`nav-item ${activeTab === 'audit' ? 'active' : ''}`}
            onClick={() => setActiveTab('audit')}
          >
            <div className="nav-item-content">
              <FileText size={18} />
              <span>Audit Trail</span>
            </div>
          </button>
        </nav>

        <div className="user-profile">
          <div className="user-avatar">VA</div>
          <div className="user-info">
            <div className="name">Vishal Aryan</div>
            <div className="role">Owner • Strategic Oversight</div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Header */}
        <header className="header">
          <div>
            <h2>
              {activeTab === 'overview' && 'Executive Virtual Management'}
              {activeTab === 'approvals' && 'Human-in-the-Loop Approval Queue'}
              {activeTab === 'command' && 'AI CEO Directive Center'}
              {activeTab === 'fleet' && 'Specialized Agent Fleet'}
              {activeTab === 'audit' && 'Immutable Audit Logs'}
            </h2>
            <p>Multi-Agent operations with strict Human-In-The-Loop authorization gates.</p>
          </div>

          <div className="system-status-bar">
            <div className="status-pill">
              <div className={`status-dot ${health?.database_connected ? 'active' : 'idle'}`} />
              <span>Atlas DB: {health?.database_connected ? 'Online' : 'Degraded'}</span>
            </div>
            <div className="status-pill">
              <div className={`status-dot ${health?.redis_connected ? 'active' : 'idle'}`} />
              <span>Redis: {health?.redis_connected ? 'Active' : 'Local'}</span>
            </div>
            <div className="status-pill">
              <div className={`status-dot ${health?.kafka_connected ? 'active' : 'idle'}`} />
              <span>Kafka: {health?.kafka_connected ? 'Streaming' : 'Local'}</span>
            </div>
          </div>
        </header>

        {actionMsg && (
          <div style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            color: '#34d399',
            padding: '12px 18px',
            borderRadius: '10px',
            marginBottom: '20px',
            fontSize: '0.9rem'
          }}>
            {actionMsg}
          </div>
        )}

        {/* METRICS ROW */}
        <div className="metrics-grid">
          <div className="metric-card amber">
            <div className="icon-wrap"><AlertCircle size={20} /></div>
            <div className="value">{pendingCount}</div>
            <div className="label">Pending HITL Approvals</div>
          </div>

          <div className="metric-card emerald">
            <div className="icon-wrap"><CheckCircle2 size={20} /></div>
            <div className="value">6</div>
            <div className="label">Active Autonomous Agents</div>
          </div>

          <div className="metric-card purple">
            <div className="icon-wrap"><DollarSign size={20} /></div>
            <div className="value">₹14.5L</div>
            <div className="label">Monthly Revenue Managed</div>
          </div>

          <div className="metric-card cyan">
            <div className="icon-wrap"><ShieldCheck size={20} /></div>
            <div className="value">100%</div>
            <div className="label">Compliance Guardrails</div>
          </div>
        </div>

        {/* AI COMMAND BOX (Visible on Overview & Command) */}
        {(activeTab === 'overview' || activeTab === 'command') && (
          <div className="command-box">
            <h3><Sparkles size={18} color="#818cf8" /> Submit Strategic Directive to AI CEO</h3>
            <p>Enter an executive instruction. The AI CEO will parse intent, and the Supervisor will coordinate workers.</p>
            
            <form onSubmit={handleLaunchGoal} className="command-input-row">
              <input
                type="text"
                className="command-input"
                placeholder="e.g. Draft monthly client invoice for Acme Corp and prepare notification email..."
                value={goalInput}
                onChange={(e) => setGoalInput(e.target.value)}
                disabled={taskInProgress}
              />
              <button type="submit" className="btn-primary" disabled={taskInProgress || !goalInput.trim()}>
                {taskInProgress ? (
                  <>
                    <RefreshCw className="animate-spin" size={16} />
                    <span>Orchestrating...</span>
                  </>
                ) : (
                  <>
                    <Send size={16} />
                    <span>Execute</span>
                  </>
                )}
              </button>
            </form>

            {/* Live Task Result Stepper */}
            {runningTask && (
              <div className="task-live-box">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ fontSize: '0.92rem' }}>Task Execution Plan & Trace:</strong>
                  <span className="type-pill" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8' }}>
                    Status: {runningTask.status}
                  </span>
                </div>
                <div className="task-steps">
                  {runningTask.steps?.map((step, idx) => (
                    <div key={idx} className="task-step">
                      <span className="agent-tag">{step.agent}</span>
                      <ArrowRight size={14} color="#64748b" />
                      <span>{step.action}</span>
                    </div>
                  ))}
                </div>
                {runningTask.summary && (
                  <p style={{ marginTop: '12px', fontSize: '0.86rem', color: '#94a3b8' }}>
                    💡 <em>{runningTask.summary}</em>
                  </p>
                )}
              </div>
            )}
          </div>
        )}

        {/* HITL APPROVALS SECTION */}
        {(activeTab === 'overview' || activeTab === 'approvals') && (
          <div>
            <div className="section-header">
              <h3>Human-in-the-Loop Pending Approvals ({pendingCount})</h3>
            </div>

            {approvals.filter(a => a.status === 'PENDING').length === 0 ? (
              <div style={{
                background: 'var(--bg-card)',
                padding: '30px',
                borderRadius: '12px',
                textAlign: 'center',
                color: '#64748b',
                border: '1px dashed var(--border-subtle)',
                marginBottom: '32px'
              }}>
                <CheckCircle2 size={32} color="#10b981" style={{ margin: '0 auto 10px' }} />
                <p>All items have been reviewed. No pending approvals in queue.</p>
              </div>
            ) : (
              <div className="approvals-grid">
                {approvals.filter(a => a.status === 'PENDING').map((ticket) => (
                  <div key={ticket.id} className="approval-card">
                    <div>
                      <div className="approval-card-top">
                        <div className="approval-title">{ticket.title}</div>
                        <span className={`type-pill ${
                          ticket.approval_type === 'INVOICE' ? 'invoice' :
                          ticket.approval_type === 'CLIENT_EMAIL' ? 'email' :
                          ticket.approval_type === 'PAYROLL' ? 'payroll' : 'compliance'
                        }`}>
                          {ticket.approval_type}
                        </span>
                      </div>

                      <p style={{ fontSize: '0.84rem', color: '#94a3b8', marginBottom: '12px' }}>
                        {ticket.description}
                      </p>

                      <div className="approval-payload-preview">
                        {JSON.stringify(ticket.payload, null, 2)}
                      </div>
                    </div>

                    <div className="approval-actions">
                      <button
                        className="btn-approve"
                        onClick={() => handleApprovalAction(ticket.id, 'APPROVE')}
                      >
                        <Check size={16} /> Approve & Release
                      </button>
                      <button
                        className="btn-reject"
                        onClick={() => handleApprovalAction(ticket.id, 'REJECT')}
                      >
                        <X size={16} /> Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* AGENT FLEET GRID (Visible on Fleet & Overview) */}
        {(activeTab === 'overview' || activeTab === 'fleet') && (
          <div>
            <div className="section-header">
              <h3>Specialized Worker Agent Fleet</h3>
            </div>

            <div className="agents-grid">
              <div className="agent-status-card">
                <div className="agent-card-header">
                  <div className="agent-name">Comms Agent</div>
                  <span className="type-pill email">Active</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Drafts client emails, qualifies leads, manages communication logs.
                </p>
                <div className="agent-tools">
                  <span className="tool-tag">Gmail API</span>
                  <span className="tool-tag">WhatsApp Cloud</span>
                  <span className="tool-tag">Zoho CRM</span>
                </div>
              </div>

              <div className="agent-status-card">
                <div className="agent-card-header">
                  <div className="agent-name">Finance Agent</div>
                  <span className="type-pill invoice">Active</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Drafts Zoho invoices, calculates 18% GST, categorizes business expenses.
                </p>
                <div className="agent-tools">
                  <span className="tool-tag">Zoho Books</span>
                  <span className="tool-tag">GST Engine</span>
                  <span className="tool-tag">Read-Only Banking</span>
                </div>
              </div>

              <div className="agent-status-card">
                <div className="agent-card-header">
                  <div className="agent-name">Compliance Agent</div>
                  <span className="type-pill compliance">Active</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Tracks MCA/ROC statutory deadlines, Form 8 & Form 11 filings.
                </p>
                <div className="agent-tools">
                  <span className="tool-tag">Pinecone RAG</span>
                  <span className="tool-tag">MCA Calendar</span>
                  <span className="tool-tag">Partner Alerts</span>
                </div>
              </div>

              <div className="agent-status-card">
                <div className="agent-card-header">
                  <div className="agent-name">Project Agent</div>
                  <span className="type-pill email">Active</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Syncs Notion task boards, detects blocked milestones, generates status updates.
                </p>
                <div className="agent-tools">
                  <span className="tool-tag">Notion API</span>
                  <span className="tool-tag">n8n Webhooks</span>
                </div>
              </div>

              <div className="agent-status-card">
                <div className="agent-card-header">
                  <div className="agent-name">HR Agent</div>
                  <span className="type-pill payroll">Active</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Tracks employee leaves, coordinates onboarding checklists, drafts monthly payroll.
                </p>
                <div className="agent-tools">
                  <span className="tool-tag">Leave Tracker</span>
                  <span className="tool-tag">Draft Payroll</span>
                </div>
              </div>

              <div className="agent-status-card">
                <div className="agent-card-header">
                  <div className="agent-name">Analytics Agent</div>
                  <span className="type-pill invoice">Active</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Compiles monthly P&L summaries, cash flow forecasts, executive dashboards.
                </p>
                <div className="agent-tools">
                  <span className="tool-tag">P&L Generator</span>
                  <span className="tool-tag">Mongo Aggregation</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* AUDIT LOG TABLE (Visible on Audit & Overview) */}
        {(activeTab === 'overview' || activeTab === 'audit') && (
          <div>
            <div className="section-header">
              <h3>Immutable Audit Trail (MongoDB Atlas + Kafka Stream)</h3>
            </div>

            <div className="audit-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Actor</th>
                    <th>Type</th>
                    <th>Action</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.map((log, idx) => (
                    <tr key={idx}>
                      <td style={{ color: '#64748b', fontSize: '0.78rem' }}>
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </td>
                      <td style={{ fontWeight: 600 }}>{log.agent_name || log.actor_id}</td>
                      <td>
                        <span className="type-pill" style={{
                          background: log.actor_type === 'AGENT' ? 'rgba(99, 102, 241, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                          color: log.actor_type === 'AGENT' ? '#818cf8' : '#34d399'
                        }}>
                          {log.actor_type}
                        </span>
                      </td>
                      <td><code>{log.action}</code></td>
                      <td><span className="status-badge-success">{log.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
