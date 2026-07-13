import { type FormEvent, useEffect, useRef, useState } from 'react'
import { Activity, BadgeCheck, BarChart3, ChevronRight, CircleUserRound, FileSearch, Fingerprint, Languages, LayoutDashboard, Link2, LockKeyhole, MapPin, Menu, Mic, Search, Send, ShieldCheck, Sparkles, Upload, X } from 'lucide-react'
import './workspace.css'

const API = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '')
type Page = 'chat' | 'dashboard' | 'linked' | 'ingestion'
type Citation = { record_id: string; fir_number: string; district: string; station: string }
type Message = { side: 'user' | 'ai'; text: string; citations?: Citation[]; confidence?: string; auditId?: number }
type Fir = { id: string; fir_number: string; district: string; station: string; date: string; status: string; outcome?: string; narrative_en?: string; narrative_kn?: string; ipc_sections?: string[]; mo_elements?: string[]; similarity?: number; shared_elements?: string[] }
type Dashboard = { total_visible: number; by_district: { district: string; count: number }[]; recent: Fir[]; fairness_note: string }
type SimilarityResult = { source: { id: string; fir_number: string }; matches: Fir[]; method: string }
type IngestionResult = { status: string; filename: string; language: string; extracted: { fir_number: string | null; station: string | null; narrative: string }; persisted: boolean; scope_note: string }

const suggestions = [
  'Show similar MO cases for FIR-2024-0100',
  'How many IPC 420 cases are in Mysuru?',
  'ಮೈಸೂರು ಜಿಲ್ಲೆಯಲ್ಲಿ ಎಷ್ಟು ಪ್ರಕರಣಗಳು?',
]
const pageTitles: Record<Page, string> = { chat: 'Crime Intelligence', dashboard: 'Operations Overview', linked: 'Linked Cases', ingestion: 'FIR Ingestion' }
const pages = new Set<Page>(['chat', 'dashboard', 'linked', 'ingestion'])
function pageFromHash(): Page {
  const value = window.location.hash.replace('#', '') as Page
  return pages.has(value) ? value : 'chat'
}

async function apiJson<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, options)
  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try { detail = (await response.json()).detail || detail } catch { /* non-JSON response */ }
    throw new Error(detail)
  }
  return response.json()
}

function App() {
  const [page, setPage] = useState<Page>(pageFromHash)
  const [mobileNav, setMobileNav] = useState(false)
  const [lang, setLang] = useState<'EN' | 'ಕಂ'>('EN')
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [audit, setAudit] = useState<any[] | null>(null)
  const [caseState, setCaseState] = useState<{ loading: boolean; error?: string; data?: Fir } | null>(null)
  const [messages, setMessages] = useState<Message[]>([{ side: 'ai', text: 'Namaskara. I’m PRAHARI — your grounded crime intelligence assistant. Ask about FIR patterns, case links, IPC sections, or cross-station modus operandi. Every claim is tied to a source record.' }])
  const [dash, setDash] = useState<Dashboard | null>(null)
  const conversation = useRef(crypto.randomUUID())

  useEffect(() => { apiJson<Dashboard>('/api/dashboard').then(setDash).catch(() => {}) }, [])
  useEffect(() => { const sync = () => setPage(pageFromHash()); window.addEventListener('hashchange', sync); return () => window.removeEventListener('hashchange', sync) }, [])
  function navigate(next: Page) { setPage(next); window.location.hash = next === 'chat' ? '' : next; setMobileNav(false) }

  async function send(value = input) {
    if (!value.trim() || loading) return
    setMessages(items => [...items, { side: 'user', text: value }]); setInput(''); setLoading(true)
    try {
      const data = await apiJson<any>('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: value, conversation_id: conversation.current, language: lang === 'ಕಂ' ? 'kn' : undefined }) })
      setMessages(items => [...items, { side: 'ai', text: data.answer, citations: data.citations, confidence: data.confidence, auditId: data.audit_id }])
    } catch (error) {
      setMessages(items => [...items, { side: 'ai', text: error instanceof Error ? error.message : 'The intelligence service is unavailable.' }])
    } finally { setLoading(false) }
  }
  async function explain() {
    try { setAudit((await apiJson<any>(`/api/audit/${conversation.current}`)).chain) } catch { setAudit([]) }
  }
  async function openCase(id: string) {
    setCaseState({ loading: true })
    try { setCaseState({ loading: false, data: await apiJson<Fir>(`/api/cases/${encodeURIComponent(id)}`) }) }
    catch (error) { setCaseState({ loading: false, error: error instanceof Error ? error.message : 'Unable to load FIR.' }) }
  }

  return <div className="shell">
    {mobileNav && <button className="nav-scrim" aria-label="Close navigation" onClick={() => setMobileNav(false)} />}
    <aside className={mobileNav ? 'open' : ''}>
      <div className="brand"><div className="crest"><ShieldCheck /></div><div><b>PRAHARI</b><span>ಪ್ರಹರಿ · SCRB Karnataka</span></div></div>
      <nav aria-label="Primary navigation">
        <button className={page === 'chat' ? 'active' : ''} onClick={() => navigate('chat')}><Sparkles /> Intelligence Chat</button>
        <button className={page === 'dashboard' ? 'active' : ''} onClick={() => navigate('dashboard')}><LayoutDashboard /> Operations Overview</button>
        <button className={page === 'linked' ? 'active' : ''} onClick={() => navigate('linked')}><Link2 /> Linked Cases <em>Beta</em></button>
        <button className={page === 'ingestion' ? 'active' : ''} onClick={() => navigate('ingestion')}><FileSearch /> FIR Ingestion</button>
      </nav>
      <div className="secure"><LockKeyhole /><div><b>Secure workspace</b><span>Hash-chained audit enabled</span></div></div>
      <div className="profile"><CircleUserRound /><div><b>SCRB Demo Officer</b><span>State-wide access</span></div><ChevronRight /></div>
    </aside>
    <main>
      <header><button className="mobile" aria-label="Open navigation" onClick={() => setMobileNav(true)}><Menu /></button><div><span className="eyebrow">Karnataka State Police</span><h1>{pageTitles[page]}</h1></div><div className="header-actions"><span className="live"><i /> Systems operational</span><button className="language" onClick={() => setLang(lang === 'EN' ? 'ಕಂ' : 'EN')}><Languages /> {lang}</button></div></header>
      {page === 'chat' && <ChatView messages={messages} loading={loading} input={input} lang={lang} setInput={setInput} send={send} explain={explain} openCase={openCase} />}
      {page === 'dashboard' && <DashboardView data={dash} openCase={openCase} />}
      {page === 'linked' && <LinkedCasesView initialId={dash?.recent?.[0]?.id} openCase={openCase} />}
      {page === 'ingestion' && <IngestionView />}
    </main>
    {audit && <div className="modal-bg" onClick={() => setAudit(null)}><div className="modal" onClick={e => e.stopPropagation()}><div className="modal-head"><div><span className="eyebrow">Evidence trail</span><h2>Why this answer?</h2></div><button aria-label="Close" onClick={() => setAudit(null)}><X /></button></div>{audit.length ? audit.map(x => <div className="audit-row" key={x.id}><span className={x.verified ? 'verified' : ''}><BadgeCheck /> {x.verified ? 'Verified' : 'Failed'}</span><b>{x.query}</b><small>{x.record_ids.length} records · {x.entry_hash.slice(0, 18)}…</small></div>) : <div className="empty-state">No audit entries are available yet.</div>}</div></div>}
    {caseState && <CaseModal state={caseState} close={() => setCaseState(null)} />}
  </div>
}

function ChatView({ messages, loading, input, lang, setInput, send, explain, openCase }: { messages: Message[]; loading: boolean; input: string; lang: string; setInput: (v: string) => void; send: (v?: string) => void; explain: () => void; openCase: (id: string) => void }) {
  return <section className="chat-page"><div className="context"><div><Activity /><span><b>Grounded analysis</b> · Results are restricted to retrieved records</span></div><span>Jurisdiction: Karnataka</span></div>
    <div className="messages">{messages.map((m, i) => <div className={`message ${m.side}`} key={i}>{m.side === 'ai' && <div className="avatar"><Fingerprint /></div>}<div className="bubble">{m.side === 'ai' && <label>PRAHARI INTELLIGENCE</label>}<p>{m.text}</p>{m.citations && m.citations.length > 0 && <div className="citations">{m.citations.slice(0, 5).map(c => <button onClick={() => openCase(c.record_id)} title={`${c.station}, ${c.district}`} key={c.record_id}><BadgeCheck /> {c.record_id}</button>)}</div>}{m.auditId && <div className="answer-meta"><span className={`confidence ${m.confidence}`}>{m.confidence} confidence</span><button onClick={explain}><ShieldCheck /> Explain this answer</button></div>}</div></div>)}{loading && <div className="typing"><i /><i /><i /> Searching verified records</div>}</div>
    {messages.length === 1 && <div className="suggestions">{suggestions.map((s, i) => <button key={s} onClick={() => send(s)}><span>{i === 0 ? <Link2 /> : i === 1 ? <BarChart3 /> : <Languages />}</span>{s}<ChevronRight /></button>)}</div>}
    <div className="composer"><div className="input"><textarea value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }} placeholder={lang === 'EN' ? 'Ask a question about crime records…' : 'ಅಪರಾಧ ದಾಖಲೆಗಳ ಬಗ್ಗೆ ಪ್ರಶ್ನಿಸಿ…'} /><button className="mic" title="Voice input"><Mic /></button><button className="send" onClick={() => send()} disabled={!input.trim() || loading}><Send /></button></div><p><ShieldCheck /> Responses cite retrieved FIR records. Verify operational decisions independently.</p></div>
  </section>
}

function DashboardView({ data, openCase }: { data: Dashboard | null; openCase: (id: string) => void }) {
  const max = Math.max(1, ...(data?.by_district.map(x => x.count) || [1]))
  return <section className="dashboard"><div className="fairness"><ShieldCheck /><div><b>Ethical analytics by design</b><span>{data?.fairness_note || 'PRAHARI displays area aggregates only — never individual risk scores.'}</span></div></div><div className="stats"><article><span>Visible records</span><strong>{data?.total_visible ?? '—'}</strong><small>Within current jurisdiction</small></article><article><span>Active districts</span><strong>{data?.by_district.length ?? '—'}</strong><small>Aggregated case coverage</small></article><article><span>Audit integrity</span><strong>100%</strong><small>Verified interaction chain</small></article></div><div className="dash-grid"><div className="panel"><div className="panel-title"><div><span className="eyebrow">Area-level distribution</span><h2>Cases by district</h2></div><MapPin /></div><div className="bars">{data?.by_district.slice(0, 8).map(d => <div className="bar-row" key={d.district}><span>{d.district}</span><div><i style={{ width: `${Math.max(16, d.count / max * 100)}%` }} /></div><b>{d.count}</b></div>)}</div></div><div className="panel"><div className="panel-title"><div><span className="eyebrow">Latest intelligence</span><h2>Recent FIRs</h2></div><FileSearch /></div>{data?.recent.map(r => <button className="recent" onClick={() => openCase(r.id)} key={r.id}><span>{r.id.slice(-4)}</span><div><b>{r.fir_number}</b><small>{r.station} · {r.district}</small></div><em>{r.status}</em></button>)}</div></div></section>
}

function LinkedCasesView({ initialId, openCase }: { initialId?: string; openCase: (id: string) => void }) {
  const [caseId, setCaseId] = useState('')
  const [result, setResult] = useState<SimilarityResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => { if (initialId && !caseId) setCaseId(initialId) }, [initialId, caseId])
  async function search(e?: FormEvent) {
    e?.preventDefault(); if (!caseId.trim()) return
    setLoading(true); setError(''); setResult(null)
    try { setResult(await apiJson<SimilarityResult>(`/api/cases/${encodeURIComponent(caseId.trim().toUpperCase())}/similar`)) }
    catch (err) { setError(err instanceof Error ? err.message : 'Unable to analyze linked cases.') }
    finally { setLoading(false) }
  }
  return <section className="workspace-page"><div className="page-intro"><div><span className="eyebrow">Explainable MO analysis</span><h2>Cross-station linked cases</h2><p>Compare modus-operandi elements across FIRs. Results exclude the originating station and show the shared evidence behind every score.</p></div><Link2 /></div>
    <form className="search-card" onSubmit={search}><label htmlFor="case-id">Source FIR ID</label><div><input id="case-id" value={caseId} onChange={e => setCaseId(e.target.value)} placeholder="e.g. FIR-2025-0421" /><button disabled={loading || !caseId.trim()}>{loading ? 'Analyzing…' : <><Search /> Find linked cases</>}</button></div><small>Use a PRAHARI record ID shown on any citation or recent-FIR card.</small></form>
    {error && <div className="error-state"><b>Analysis unavailable</b><span>{error} Check the FIR ID and try again.</span></div>}
    {result && <div className="results-panel"><div className="results-head"><div><span className="eyebrow">Source record</span><button onClick={() => openCase(result.source.id)}>{result.source.id} · {result.source.fir_number}</button></div><span>{result.matches.length} cross-station matches</span></div>{result.matches.length ? <div className="match-grid">{result.matches.map(match => <article key={match.id}><div className="match-score"><strong>{Math.round((match.similarity || 0) * 100)}%</strong><span>MO similarity</span></div><button className="record-link" onClick={() => openCase(match.id)}>{match.id}</button><p>{match.station} · {match.district}</p><div className="tags">{match.shared_elements?.map(item => <span key={item}>{item}</span>)}</div><small>{match.status}</small></article>)}</div> : <div className="empty-state">No cross-station cases met the explainable similarity threshold.</div>}<p className="method"><ShieldCheck /> {result.method}</p></div>}
  </section>
}

function IngestionView() {
  const [file, setFile] = useState<File | null>(null)
  const [language, setLanguage] = useState('auto')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<IngestionResult | null>(null)
  async function submit(e: FormEvent) {
    e.preventDefault(); if (!file) return
    setLoading(true); setError(''); setResult(null)
    const body = new FormData(); body.append('file', file); body.append('language', language)
    try { setResult(await apiJson<IngestionResult>('/api/ingest/scanned-fir', { method: 'POST', body })) }
    catch (err) { setError(err instanceof Error ? err.message : 'The FIR could not be processed.') }
    finally { setLoading(false) }
  }
  return <section className="workspace-page"><div className="page-intro"><div><span className="eyebrow">Human-confirmed extraction</span><h2>Scanned FIR ingestion</h2><p>Upload a scanned FIR for OCR-assisted field extraction. Nothing is persisted until an authorized operator reviews and confirms it.</p></div><FileSearch /></div>
    <form className="upload-card" onSubmit={submit}><label className="drop-zone"><Upload /><b>{file ? file.name : 'Choose a scanned FIR'}</b><span>PDF, PNG, JPG or WEBP · maximum 10 MB</span><input type="file" accept="application/pdf,image/png,image/jpeg,image/webp" onChange={e => { const selected = e.target.files?.[0] || null; if (selected && selected.size > 10 * 1024 * 1024) { setFile(null); setError('File exceeds the 10 MB upload limit.') } else { setFile(selected); setError('') } }} /></label><div className="ingest-actions"><label>Document language<select value={language} onChange={e => setLanguage(e.target.value)}><option value="auto">Auto-detect</option><option value="en">English</option><option value="kn">Kannada</option></select></label><button disabled={!file || loading}>{loading ? 'Extracting…' : <><FileSearch /> Extract for review</>}</button></div></form>
    {error && <div className="error-state"><b>Upload failed</b><span>{error}</span></div>}
    {result && <div className="review-card"><div className="review-head"><div><span className="eyebrow">Operator review required</span><h2>Extraction preview</h2></div><span>{result.persisted ? 'Persisted' : 'Not persisted'}</span></div><dl><div><dt>File</dt><dd>{result.filename}</dd></div><div><dt>Detected language</dt><dd>{result.language}</dd></div><div><dt>FIR number</dt><dd>{result.extracted.fir_number || 'Not detected'}</dd></div><div><dt>Police station</dt><dd>{result.extracted.station || 'Not detected'}</dd></div><div className="wide"><dt>Extracted narrative</dt><dd>{result.extracted.narrative}</dd></div></dl><p><ShieldCheck /> {result.scope_note}</p></div>}
  </section>
}

function CaseModal({ state, close }: { state: { loading: boolean; error?: string; data?: Fir }; close: () => void }) {
  return <div className="modal-bg" onClick={close}><div className="modal case-modal" onClick={e => e.stopPropagation()}><div className="modal-head"><div><span className="eyebrow">Verified FIR record</span><h2>{state.data?.id || 'FIR details'}</h2></div><button aria-label="Close" onClick={close}><X /></button></div>{state.loading ? <div className="empty-state">Loading verified record…</div> : state.error ? <div className="error-state"><b>Record unavailable</b><span>{state.error}</span></div> : state.data && <><div className="case-meta"><span>{state.data.fir_number}</span><span>{state.data.station}</span><span>{state.data.district}</span><span>{state.data.date}</span></div><dl><div><dt>Status</dt><dd>{state.data.status}</dd></div><div><dt>Outcome</dt><dd>{state.data.outcome || 'Pending'}</dd></div><div><dt>IPC sections</dt><dd>{state.data.ipc_sections?.join(', ') || 'Not recorded'}</dd></div><div className="wide"><dt>MO elements</dt><dd>{state.data.mo_elements?.join(' · ') || 'Not recorded'}</dd></div><div className="wide"><dt>Narrative</dt><dd>{state.data.narrative_en || 'Not available'}</dd></div></dl></>}</div></div>
}

export default App
