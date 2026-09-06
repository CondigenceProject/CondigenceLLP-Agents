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
  Layers,
  History,
  ChevronRight,
  Code2
} from 'lucide-react';

const QUICK_DIRECTIVES = [
  { label: '💰 Invoice & Email', prompt: 'Draft monthly client invoice for Acme Global Corp for ₹50,000 and prepare notification email' },
  { label: '🛡️ Form 11 Compliance', prompt: 'Check MCA statutory compliance deadline for Form 11 Annual Return and prepare sign-off dossier' },
  { label: '👥 August Payroll', prompt: 'Calculate August payroll disbursement and prepare HR approval request' },
  { label: '📊 Q3 P&L Report', prompt: 'Generate Q3 P&L report, margin breakdown, and cash flow health analysis' },
  { label: '📁 Sync Notion Board', prompt: 'Sync Notion project board, detect blocked milestones and report sprint progress' }
];

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [health, setHealth] = useState(null);
  const [serverOnline, setServerOnline] = useState(true);
  const [approvals, setApprovals] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [tasksHistory, setTasksHistory] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [actionMsg, setActionMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Command Center Goal execution state
  const [goalInput, setGoalInput] = useState('');
  const [runningTask, setRunningTask] = useState(null);
  const [taskInProgress, setTaskInProgress] = useState(false);

  // Fetch initial data
  const fetchData = async () => {
    try {
      // 1. Health
      const hRes = await fetch(`${API_BASE}/health`);
      if (hRes.ok) {
        setHealth(await hRes.json());
        setServerOnline(true);
      } else {
        setServerOnline(false);
      }

      // 2. Approvals
      const appRes = await fetch(`${API_BASE}/api/v1/approvals`);
      if (appRes.ok) setApprovals(await appRes.json());

      // 3. Audit Logs
      const aRes = await fetch(`${API_BASE}/api/v1/audit/logs?limit=30`);
      if (aRes.ok) setAuditLogs(await aRes.json());

      // 4. Task History
      const tRes = await fetch(`${API_BASE}/api/v1/agents/tasks`);
      if (tRes.ok) {
        const tasks = await tRes.json();
        setTasksHistory(tasks);
      }
    } catch (e) {
      console.error('Error fetching dashboard data:', e);
      setServerOnline(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, []);

  // Handle Goal Launch
  const handleLaunchGoal = async (e, customPrompt = null) => {
    if (e && e.preventDefault) e.preventDefault();
    const targetGoal = (customPrompt !== null ? customPrompt : goalInput).trim();
    if (!targetGoal) return;

    setTaskInProgress(true);
    setRunningTask(null);
    setActionMsg('');
    setErrorMsg('');

    try {
      const res = await fetch(`${API_BASE}/api/v1/agents/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal: targetGoal,
          requester_role: 'OWNER',
          context: {}
        })
      });

      if (res.ok) {
        const data = await res.json();
        setRunningTask(data);
        setSelectedTask(data);
        if (!customPrompt) setGoalInput('');
        setActionMsg(`✅ Strategic Directive successfully executed across ${data.steps?.length || 0} agents!`);
        fetchData();
        setTimeout(() => setActionMsg(''), 5000);
      } else {
        const errJson = await res.json().catch(() => ({ detail: res.statusText }));
        setErrorMsg(`Execution Failed (${res.status}): ${errJson.detail || 'Server could not complete multi-agent workflow.'}`);
      }
    } catch (err) {
      console.error('Task launch failed:', err);
      setErrorMsg(`Connection Error: Cannot communicate with the FastAPI backend at ${API_BASE || 'http://127.0.0.1:8000'}.`);
      setServerOnline(false);
    } finally {
      setTaskInProgress(false);
    }
  };

  // Handle Approval Action
  const handleApprovalAction = async (ticketId, action) => {
    setErrorMsg('');
    try {
      const res = await fetch(`${API_BASE}/api/v1/approvals/${ticketId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: action,
          notes: `Actioned via Owner Portal by Admin`
        })
      });
      if (res.ok) {
        setActionMsg(`Ticket ${ticketId} was successfully ${action.toLowerCase()}d.`);
        fetchData();
        setTimeout(() => setActionMsg(''), 4000);
      } else {
        const errJson = await res.json().catch(() => ({ detail: res.statusText }));
        setErrorMsg(`Approval Action Failed (${res.status}): ${errJson.detail || 'Could not update ticket status.'}`);
      }
    } catch (err) {
      console.error('Approval action error:', err);
      setErrorMsg(`Failed to connect to approval service: ${err.message}`);
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
            className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <div className="nav-item-content">
              <History size={18} />
              <span>Task History</span>
            </div>
            {tasksHistory.length > 0 && <span className="nav-badge" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8' }}>{tasksHistory.length}</span>}
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
          <div className="user-avatar">AD</div>
          <div className="user-info">
            <div className="name">Admin</div>
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
              {activeTab === 'history' && 'Agent Execution & Directive History'}
              {activeTab === 'fleet' && 'Specialized Agent Fleet'}
              {activeTab === 'audit' && 'Immutable Audit Logs'}
            </h2>
            <p>Multi-Agent operations with strict Human-In-The-Loop authorization gates.</p>
          </div>

          <div className="system-status-bar">
            <div className="status-pill">
              <div className={`status-dot ${serverOnline ? 'active' : 'idle'}`} />
              <span>Backend API: {serverOnline ? 'Connected' : 'Offline'}</span>
            </div>
            <div className="status-pill">
              <div className={`status-dot ${health?.database_connected ? 'active' : 'idle'}`} />
              <span>Atlas DB: {health?.database_connected ? 'Online' : 'Mock/Local'}</span>
            </div>
            <div className="status-pill">
              <div className={`status-dot ${health?.redis_connected ? 'active' : 'idle'}`} />
              <span>Redis: {health?.redis_connected ? 'Active' : 'Local'}</span>
            </div>
          </div>
        </header>

        {/* BACKEND OFFLINE ALERT */}
        {!serverOnline && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            color: '#f87171',
            padding: '14px 18px',
            borderRadius: '10px',
            marginBottom: '20px',
            fontSize: '0.88rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <AlertCircle size={20} />
              <span>
                <strong>Backend Server Disconnected:</strong> FastAPI backend is not running at <code>http://127.0.0.1:8000</code>. Start it with <code>python main.py</code> in your project root to run agents.
              </span>
            </div>
            <button
              className="btn-secondary"
              onClick={fetchData}
              style={{ fontSize: '0.8rem', padding: '6px 12px', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <RefreshCw size={14} /> Reconnect
            </button>
          </div>
        )}

        {actionMsg && (
          <div style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            color: '#34d399',
            padding: '12px 18px',
            borderRadius: '10px',
            marginBottom: '20px',
            fontSize: '0.9rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <span>{actionMsg}</span>
            <button onClick={() => setActionMsg('')} style={{ background: 'none', border: 'none', color: '#34d399', cursor: 'pointer' }}>
              <X size={16} />
            </button>
          </div>
        )}

        {errorMsg && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            color: '#f87171',
            padding: '12px 18px',
            borderRadius: '10px',
            marginBottom: '20px',
            fontSize: '0.9rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertCircle size={18} />
              <span>{errorMsg}</span>
            </div>
            <button onClick={() => setErrorMsg('')} style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer' }}>
              <X size={16} />
            </button>
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
            <div className="icon-wrap"><History size={20} /></div>
            <div className="value">{tasksHistory.length}</div>
            <div className="label">Total Directives Executed</div>
          </div>
        </div>

        {/* AI COMMAND BOX (Visible on Overview & Command) */}
        {(activeTab === 'overview' || activeTab === 'command') && (
          <div className="command-box">
            <h3><Sparkles size={18} color="#818cf8" /> Submit Strategic Directive to AI CEO</h3>
            <p>Enter an executive instruction. The AI CEO will parse intent, and the Supervisor will coordinate workers.</p>

            {/* Quick Directive Templates */}
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '14px' }}>
              <span style={{ fontSize: '0.8rem', color: '#64748b', alignSelf: 'center', marginRight: '4px' }}>Quick Prompts:</span>
              {QUICK_DIRECTIVES.map((tpl, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => {
                    setGoalInput(tpl.prompt);
                    handleLaunchGoal(null, tpl.prompt);
                  }}
                  disabled={taskInProgress}
                  style={{
                    background: 'rgba(99, 102, 241, 0.1)',
                    border: '1px solid rgba(99, 102, 241, 0.25)',
                    color: '#a5b4fc',
                    borderRadius: '20px',
                    padding: '4px 12px',
                    fontSize: '0.78rem',
                    cursor: taskInProgress ? 'not-allowed' : 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(99, 102, 241, 0.25)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(99, 102, 241, 0.1)'; }}
                >
                  {tpl.label}
                </button>
              ))}
            </div>
            
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
                  <strong style={{ fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Sparkles size={16} color="#818cf8" />
                    Task Execution Plan & Trace:
                  </strong>
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
                  <p style={{ marginTop: '12px', fontSize: '0.88rem', color: '#94a3b8' }}>
                    💡 <em>{runningTask.summary}</em>
                  </p>
                )}

                {/* Generated Artifacts Section */}
                {runningTask.artifacts && Object.keys(runningTask.artifacts).length > 0 && (
                  <div style={{ marginTop: '18px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {/* INVOICE CARD */}
                    {runningTask.artifacts.invoice_draft && (
                      <div style={{
                        background: 'rgba(15, 23, 42, 0.7)',
                        border: '1px solid rgba(99, 102, 241, 0.3)',
                        borderRadius: '10px',
                        padding: '16px',
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                          <span style={{ fontWeight: 600, color: '#a5b4fc', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <DollarSign size={16} /> Generated Invoice Draft
                          </span>
                          <span className="type-pill invoice">{runningTask.artifacts.invoice_draft.status}</span>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '10px', fontSize: '0.84rem' }}>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>Invoice #</span>
                            <strong>{runningTask.artifacts.invoice_draft.invoice_number}</strong>
                          </div>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>Client</span>
                            <strong>{runningTask.artifacts.invoice_draft.client_name}</strong>
                          </div>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>Base Amount</span>
                            <span>₹{Number(runningTask.artifacts.invoice_draft.base_amount).toLocaleString('en-IN')}</span>
                          </div>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>GST (18%)</span>
                            <span>₹{Number(runningTask.artifacts.invoice_draft.gst_amount).toLocaleString('en-IN')}</span>
                          </div>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>Total Amount</span>
                            <strong style={{ color: '#34d399' }}>₹{Number(runningTask.artifacts.invoice_draft.total_amount).toLocaleString('en-IN')}</strong>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* COMMS / EMAIL CARD */}
                    {runningTask.artifacts.comms_draft && (
                      <div style={{
                        background: 'rgba(15, 23, 42, 0.7)',
                        border: '1px solid rgba(16, 185, 129, 0.3)',
                        borderRadius: '10px',
                        padding: '16px',
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                          <span style={{ fontWeight: 600, color: '#6ee7b7', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <Mail size={16} /> Drafted Client Email
                          </span>
                          <span className="type-pill email">{runningTask.artifacts.comms_draft.channel || 'EMAIL'}</span>
                        </div>
                        <div style={{ fontSize: '0.84rem', marginBottom: '6px' }}>
                          <span style={{ color: '#64748b' }}>To: </span>
                          <span>{runningTask.artifacts.comms_draft.recipient}</span>
                        </div>
                        <div style={{ fontSize: '0.84rem', marginBottom: '10px' }}>
                          <span style={{ color: '#64748b' }}>Subject: </span>
                          <strong>{runningTask.artifacts.comms_draft.subject}</strong>
                        </div>
                        <pre style={{
                          background: 'rgba(0, 0, 0, 0.3)',
                          padding: '12px',
                          borderRadius: '6px',
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'inherit',
                          fontSize: '0.83rem',
                          color: '#cbd5e1',
                          margin: 0
                        }}>
                          {runningTask.artifacts.comms_draft.body}
                        </pre>
                      </div>
                    )}

                    {/* PAYROLL / HR CARD */}
                    {runningTask.artifacts.payroll_draft && (
                      <div style={{
                        background: 'rgba(15, 23, 42, 0.7)',
                        border: '1px solid rgba(236, 72, 153, 0.3)',
                        borderRadius: '10px',
                        padding: '16px',
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                          <span style={{ fontWeight: 600, color: '#f472b6', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <Users size={16} /> Drafted Payroll & HR Authorization
                          </span>
                          <span className="type-pill payroll">{runningTask.artifacts.payroll_draft.status}</span>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px', fontSize: '0.84rem' }}>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>Disbursement Month</span>
                            <strong>{runningTask.artifacts.payroll_draft.month}</strong>
                          </div>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>Team Headcount</span>
                            <strong>{runningTask.artifacts.payroll_draft.employee_count} Employees</strong>
                          </div>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>Gross Payroll</span>
                            <span>₹{Number(runningTask.artifacts.payroll_draft.total_gross_disbursement).toLocaleString('en-IN')}</span>
                          </div>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>TDS Deductions</span>
                            <span>₹{Number(runningTask.artifacts.payroll_draft.statutory_deductions_tds).toLocaleString('en-IN')}</span>
                          </div>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>Net Payable</span>
                            <strong style={{ color: '#f472b6' }}>₹{Number(runningTask.artifacts.payroll_draft.net_payable).toLocaleString('en-IN')}</strong>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* COMPLIANCE CARD */}
                    {runningTask.artifacts.compliance_filing && (
                      <div style={{
                        background: 'rgba(15, 23, 42, 0.7)',
                        border: '1px solid rgba(6, 182, 212, 0.3)',
                        borderRadius: '10px',
                        padding: '16px',
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                          <span style={{ fontWeight: 600, color: '#67e8f9', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <ShieldCheck size={16} /> Statutory Compliance Dossier
                          </span>
                          <span className="type-pill compliance">{runningTask.artifacts.compliance_filing.status}</span>
                        </div>
                        <div style={{ fontSize: '0.84rem', color: '#cbd5e1', marginBottom: '6px' }}>
                          <strong>Form: </strong> {runningTask.artifacts.compliance_filing.form} | <strong>Authority: </strong> {runningTask.artifacts.compliance_filing.statutory_body}
                        </div>
                        <div style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
                          📅 Deadline: <strong>{runningTask.artifacts.compliance_filing.upcoming_deadline}</strong>
                        </div>
                      </div>
                    )}

                    {/* PROJECT / NOTION CARD */}
                    {runningTask.artifacts.project_status && (
                      <div style={{
                        background: 'rgba(15, 23, 42, 0.7)',
                        border: '1px solid rgba(168, 85, 247, 0.3)',
                        borderRadius: '10px',
                        padding: '16px',
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                          <span style={{ fontWeight: 600, color: '#c084fc', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <FolderKanban size={16} /> Project Board Sync ({runningTask.artifacts.project_status.platform})
                          </span>
                          <span className="type-pill" style={{ background: 'rgba(168, 85, 247, 0.2)', color: '#c084fc' }}>Active</span>
                        </div>
                        <p style={{ fontSize: '0.84rem', color: '#cbd5e1', margin: '4px 0 8px' }}>
                          {runningTask.artifacts.project_status.highlight}
                        </p>
                        <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                          Tasks on track: <strong>{runningTask.artifacts.project_status.tasks_on_track}</strong> | At risk: <strong>{runningTask.artifacts.project_status.tasks_at_risk}</strong>
                        </div>
                      </div>
                    )}

                    {/* ANALYTICS / P&L CARD */}
                    {runningTask.artifacts.financial_report && (
                      <div style={{
                        background: 'rgba(15, 23, 42, 0.7)',
                        border: '1px solid rgba(234, 179, 8, 0.3)',
                        borderRadius: '10px',
                        padding: '16px',
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                          <span style={{ fontWeight: 600, color: '#fde047', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <BarChart3 size={16} /> Executive P&L & Revenue Metrics
                          </span>
                          <span className="type-pill" style={{ background: 'rgba(234, 179, 8, 0.2)', color: '#fde047' }}>{runningTask.artifacts.financial_report.period}</span>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px', fontSize: '0.84rem' }}>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>Gross Revenue</span>
                            <strong style={{ color: '#34d399' }}>₹{Number(runningTask.artifacts.financial_report.gross_revenue).toLocaleString('en-IN')}</strong>
                          </div>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>OpEx</span>
                            <span>₹{Number(runningTask.artifacts.financial_report.operating_expenses).toLocaleString('en-IN')}</span>
                          </div>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>Net Margin</span>
                            <strong>{runningTask.artifacts.financial_report.net_operating_margin}</strong>
                          </div>
                          <div>
                            <span style={{ color: '#64748b', display: 'block' }}>Cash Health</span>
                            <strong style={{ color: '#38bdf8' }}>{runningTask.artifacts.financial_report.cash_flow_health}</strong>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TASK HISTORY VIEW (When History Tab is selected) */}
        {activeTab === 'history' && (
          <div>
            <div className="section-header">
              <h3>Directives & Multi-Agent Execution History ({tasksHistory.length})</h3>
              <button className="btn-secondary" onClick={fetchData} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', fontSize: '0.82rem' }}>
                <RefreshCw size={14} /> Refresh History
              </button>
            </div>

            {tasksHistory.length === 0 ? (
              <div style={{
                background: 'var(--bg-card)',
                padding: '30px',
                borderRadius: '12px',
                textAlign: 'center',
                color: '#64748b',
                border: '1px dashed var(--border-subtle)'
              }}>
                <Clock size={32} color="#6366f1" style={{ margin: '0 auto 10px' }} />
                <p>No task history yet. Submit a directive in "AI Command" to see agents in action.</p>
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: selectedTask ? '1fr 1.2fr' : '1fr', gap: '20px' }}>
                {/* Tasks List */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {tasksHistory.map((task) => (
                    <div
                      key={task.task_id}
                      onClick={() => setSelectedTask(task)}
                      style={{
                        background: selectedTask?.task_id === task.task_id ? 'rgba(99, 102, 241, 0.15)' : 'var(--bg-card)',
                        border: selectedTask?.task_id === task.task_id ? '1px solid #6366f1' : '1px solid var(--border-subtle)',
                        borderRadius: '12px',
                        padding: '16px',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                        <span style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.9rem', flex: 1, marginRight: '10px' }}>
                          {task.goal}
                        </span>
                        <span className={`type-pill ${task.status === 'COMPLETED' ? 'compliance' : 'invoice'}`}>
                          {task.status}
                        </span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', fontSize: '0.78rem', color: '#94a3b8' }}>
                        <span>🕒 {new Date(task.created_at).toLocaleTimeString()}</span>
                        <span>🤖 {task.steps?.length || 0} Agents Executed</span>
                        {task.artifacts && Object.keys(task.artifacts).length > 0 && (
                          <span style={{ color: '#34d399' }}>📦 {Object.keys(task.artifacts).length} Artifacts</span>
                        )}
                      </div>

                      {task.summary && (
                        <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '8px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {task.summary}
                        </p>
                      )}
                    </div>
                  ))}
                </div>

                {/* Selected Task Deep-Dive Panel */}
                {selectedTask && (
                  <div style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '12px',
                    padding: '20px',
                    height: 'fit-content'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px' }}>
                      <h4 style={{ margin: 0, fontSize: '0.98rem', display: 'flex', alignItems: 'center', gap: '8px', color: '#a5b4fc' }}>
                        <Sparkles size={16} /> Detailed Execution Trace
                      </h4>
                      <span className="type-pill" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8' }}>
                        {selectedTask.status}
                      </span>
                    </div>

                    <div style={{ marginBottom: '16px' }}>
                      <span style={{ color: '#64748b', fontSize: '0.8rem', display: 'block' }}>Directive:</span>
                      <p style={{ margin: '4px 0 0', fontWeight: 600, fontSize: '0.9rem' }}>{selectedTask.goal}</p>
                    </div>

                    {/* Stepper Breakdown */}
                    <div style={{ marginBottom: '18px' }}>
                      <span style={{ color: '#64748b', fontSize: '0.8rem', display: 'block', marginBottom: '8px' }}>Agent Execution Flow:</span>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        {selectedTask.steps?.map((step, idx) => (
                          <div key={idx} style={{
                            background: 'rgba(15, 23, 42, 0.6)',
                            border: '1px solid rgba(255, 255, 255, 0.05)',
                            borderRadius: '8px',
                            padding: '10px 14px'
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                              <span className="agent-tag" style={{ fontSize: '0.78rem' }}>{step.agent}</span>
                              <span style={{ fontSize: '0.75rem', color: '#34d399' }}>✓ {step.status}</span>
                            </div>
                            <div style={{ fontSize: '0.82rem', fontWeight: 500, color: '#e2e8f0', marginTop: '4px' }}>
                              Action: <code>{step.action}</code>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Generated Artifacts Visual Display */}
                    {selectedTask.artifacts && Object.keys(selectedTask.artifacts).length > 0 && (
                      <div style={{ marginTop: '14px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <span style={{ color: '#64748b', fontSize: '0.8rem', display: 'block' }}>Generated Artifacts:</span>

                        {/* INVOICE CARD */}
                        {selectedTask.artifacts.invoice_draft && (
                          <div style={{
                            background: 'rgba(15, 23, 42, 0.8)',
                            border: '1px solid rgba(99, 102, 241, 0.3)',
                            borderRadius: '8px',
                            padding: '12px',
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                              <span style={{ fontWeight: 600, color: '#a5b4fc', fontSize: '0.86rem' }}>💵 Invoice Draft</span>
                              <span className="type-pill invoice">{selectedTask.artifacts.invoice_draft.invoice_number}</span>
                            </div>
                            <div style={{ fontSize: '0.82rem', color: '#cbd5e1' }}>
                              Client: <strong>{selectedTask.artifacts.invoice_draft.client_name}</strong> | Total: <strong style={{ color: '#34d399' }}>₹{Number(selectedTask.artifacts.invoice_draft.total_amount).toLocaleString('en-IN')}</strong>
                            </div>
                          </div>
                        )}

                        {/* EMAIL CARD */}
                        {selectedTask.artifacts.comms_draft && (
                          <div style={{
                            background: 'rgba(15, 23, 42, 0.8)',
                            border: '1px solid rgba(16, 185, 129, 0.3)',
                            borderRadius: '8px',
                            padding: '12px',
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                              <span style={{ fontWeight: 600, color: '#6ee7b7', fontSize: '0.86rem' }}>✉️ Client Email Draft</span>
                              <span className="type-pill email">{selectedTask.artifacts.comms_draft.channel || 'EMAIL'}</span>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#cbd5e1', marginBottom: '4px' }}>
                              <strong>Subject: </strong>{selectedTask.artifacts.comms_draft.subject}
                            </div>
                            <pre style={{
                              background: 'rgba(0, 0, 0, 0.3)',
                              padding: '8px',
                              borderRadius: '6px',
                              fontSize: '0.78rem',
                              color: '#94a3b8',
                              whiteSpace: 'pre-wrap',
                              margin: 0
                            }}>
                              {selectedTask.artifacts.comms_draft.body}
                            </pre>
                          </div>
                        )}

                        {/* PAYROLL CARD */}
                        {selectedTask.artifacts.payroll_draft && (
                          <div style={{
                            background: 'rgba(15, 23, 42, 0.8)',
                            border: '1px solid rgba(236, 72, 153, 0.3)',
                            borderRadius: '8px',
                            padding: '12px',
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                              <span style={{ fontWeight: 600, color: '#f472b6', fontSize: '0.86rem' }}>📋 Payroll Disbursement</span>
                              <span className="type-pill payroll">{selectedTask.artifacts.payroll_draft.month}</span>
                            </div>
                            <div style={{ fontSize: '0.82rem', color: '#cbd5e1', marginBottom: '6px' }}>
                              Headcount: <strong>{selectedTask.artifacts.payroll_draft.employee_count} Employees</strong> | Net Payable: <strong style={{ color: '#f472b6' }}>₹{Number(selectedTask.artifacts.payroll_draft.net_payable).toLocaleString('en-IN')}</strong>
                            </div>
                            {selectedTask.artifacts.payroll_draft.department_breakdown && (
                              <div style={{ fontSize: '0.76rem', color: '#94a3b8', background: 'rgba(0,0,0,0.2)', padding: '6px 8px', borderRadius: '4px' }}>
                                Departments: {JSON.stringify(selectedTask.artifacts.payroll_draft.department_breakdown)}
                              </div>
                            )}
                          </div>
                        )}

                        {/* COMPLIANCE CARD */}
                        {selectedTask.artifacts.compliance_filing && (
                          <div style={{
                            background: 'rgba(15, 23, 42, 0.8)',
                            border: '1px solid rgba(6, 182, 212, 0.3)',
                            borderRadius: '8px',
                            padding: '12px',
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                              <span style={{ fontWeight: 600, color: '#67e8f9', fontSize: '0.86rem' }}>🛡️ Compliance Dossier</span>
                              <span className="type-pill compliance">{selectedTask.artifacts.compliance_filing.form}</span>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>
                              Authority: <strong>{selectedTask.artifacts.compliance_filing.statutory_body}</strong> | Deadline: <strong>{selectedTask.artifacts.compliance_filing.upcoming_deadline}</strong>
                            </div>
                          </div>
                        )}

                        {/* PROJECT CARD */}
                        {selectedTask.artifacts.project_status && (
                          <div style={{
                            background: 'rgba(15, 23, 42, 0.8)',
                            border: '1px solid rgba(168, 85, 247, 0.3)',
                            borderRadius: '8px',
                            padding: '12px',
                          }}>
                            <span style={{ fontWeight: 600, color: '#c084fc', fontSize: '0.86rem', display: 'block', marginBottom: '4px' }}>
                              📁 Project Sync ({selectedTask.artifacts.project_status.platform})
                            </span>
                            <p style={{ fontSize: '0.8rem', color: '#cbd5e1', margin: 0 }}>
                              {selectedTask.artifacts.project_status.highlight}
                            </p>
                          </div>
                        )}

                        {/* ANALYTICS CARD */}
                        {selectedTask.artifacts.financial_report && (
                          <div style={{
                            background: 'rgba(15, 23, 42, 0.8)',
                            border: '1px solid rgba(234, 179, 8, 0.3)',
                            borderRadius: '8px',
                            padding: '12px',
                          }}>
                            <span style={{ fontWeight: 600, color: '#fde047', fontSize: '0.86rem', display: 'block', marginBottom: '4px' }}>
                              📊 P&L Metrics ({selectedTask.artifacts.financial_report.period})
                            </span>
                            <div style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>
                              Revenue: <strong style={{ color: '#34d399' }}>₹{Number(selectedTask.artifacts.financial_report.gross_revenue).toLocaleString('en-IN')}</strong> | Margin: <strong>{selectedTask.artifacts.financial_report.net_operating_margin}</strong>
                            </div>
                          </div>
                        )}

                        {/* Collapsible Raw JSON Details */}
                        <details style={{ marginTop: '8px', fontSize: '0.78rem', color: '#64748b' }}>
                          <summary style={{ cursor: 'pointer', userSelect: 'none' }}>View Raw JSON Data</summary>
                          <pre style={{
                            background: 'rgba(0, 0, 0, 0.5)',
                            padding: '10px',
                            borderRadius: '6px',
                            color: '#38bdf8',
                            overflowX: 'auto',
                            maxHeight: '200px',
                            marginTop: '6px'
                          }}>
                            {JSON.stringify(selectedTask.artifacts, null, 2)}
                          </pre>
                        </details>
                      </div>
                    )}
                  </div>
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

