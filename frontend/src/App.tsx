import { useEffect, useRef, useState } from 'react'
import { Activity, BadgeCheck, BarChart3, ChevronRight, CircleUserRound, FileSearch, Fingerprint, Languages, LayoutDashboard, Link2, LockKeyhole, MapPin, Menu, Mic, Send, ShieldCheck, Sparkles } from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
type Citation={record_id:string;fir_number:string;district:string;station:string}
type Message={side:'user'|'ai';text:string;citations?:Citation[];confidence?:string;auditId?:number}
type Dashboard={total_visible:number;by_district:{district:string;count:number}[];recent:any[];fairness_note:string}

const suggestions=[
  'Show similar MO cases for FIR-2024-0100',
  'How many IPC 420 cases are in Mysuru?',
  'ಮೈಸೂರು ಜಿಲ್ಲೆಯಲ್ಲಿ ಎಷ್ಟು ಪ್ರಕರಣಗಳು?',
]

function App(){
 const [page,setPage]=useState<'chat'|'dashboard'>('chat'); const [lang,setLang]=useState('EN');
 const [input,setInput]=useState(''); const [loading,setLoading]=useState(false); const [audit,setAudit]=useState<any[]|null>(null)
 const [messages,setMessages]=useState<Message[]>([{side:'ai',text:'Namaskara. I’m PRAHARI — your grounded crime intelligence assistant. Ask about FIR patterns, case links, IPC sections, or cross-station modus operandi. Every claim is tied to a source record.'}])
 const [dash,setDash]=useState<Dashboard|null>(null); const conversation=useRef(crypto.randomUUID())
 useEffect(()=>{fetch(`${API}/api/dashboard`).then(r=>r.json()).then(setDash).catch(()=>{})},[])
 async function send(value=input){if(!value.trim()||loading)return; setMessages(m=>[...m,{side:'user',text:value}]);setInput('');setLoading(true)
  try{const r=await fetch(`${API}/api/chat`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:value,conversation_id:conversation.current,language:lang==='ಕಂ'?'kn':undefined})});if(!r.ok)throw new Error();const d=await r.json();setMessages(m=>[...m,{side:'ai',text:d.answer,citations:d.citations,confidence:d.confidence,auditId:d.audit_id}])}catch{setMessages(m=>[...m,{side:'ai',text:'The intelligence service is unavailable. Start the API on port 8000 and try again.'}])}finally{setLoading(false)}}
 async function explain(){const r=await fetch(`${API}/api/audit/${conversation.current}`);const d=await r.json();setAudit(d.chain)}
 return <div className="shell">
  <aside><div className="brand"><div className="crest"><ShieldCheck/></div><div><b>PRAHARI</b><span>ಪ್ರಹರಿ · SCRB Karnataka</span></div></div>
   <nav><button className={page==='chat'?'active':''} onClick={()=>setPage('chat')}><Sparkles/> Intelligence Chat</button><button className={page==='dashboard'?'active':''} onClick={()=>setPage('dashboard')}><LayoutDashboard/> Operations Overview</button><button><Link2/> Linked Cases <em>Beta</em></button><button><FileSearch/> FIR Ingestion</button></nav>
   <div className="secure"><LockKeyhole/><div><b>Secure workspace</b><span>Hash-chained audit enabled</span></div></div>
   <div className="profile"><CircleUserRound/><div><b>SCRB Demo Officer</b><span>State-wide access</span></div><ChevronRight/></div>
  </aside>
  <main><header><button className="mobile"><Menu/></button><div><span className="eyebrow">Karnataka State Police</span><h1>{page==='chat'?'Crime Intelligence':'Operations Overview'}</h1></div><div className="header-actions"><span className="live"><i/> Systems operational</span><button className="language" onClick={()=>setLang(lang==='EN'?'ಕಂ':'EN')}><Languages/> {lang}</button></div></header>
  {page==='chat'?<section className="chat-page"><div className="context"><div><Activity/><span><b>Grounded analysis</b> · Results are restricted to retrieved records</span></div><span>Jurisdiction: Karnataka</span></div>
   <div className="messages">{messages.map((m,i)=><div className={`message ${m.side}`} key={i}>{m.side==='ai'&&<div className="avatar"><Fingerprint/></div>}<div className="bubble">{m.side==='ai'&&<label>PRAHARI INTELLIGENCE</label>}<p>{m.text}</p>{m.citations&&m.citations.length>0&&<div className="citations">{m.citations.slice(0,5).map(c=><a href="#" title={`${c.station}, ${c.district}`} key={c.record_id}><BadgeCheck/> {c.record_id}</a>)}</div>}{m.auditId&&<div className="answer-meta"><span className={`confidence ${m.confidence}`}>{m.confidence} confidence</span><button onClick={explain}><ShieldCheck/> Explain this answer</button></div>}</div></div>)}{loading&&<div className="typing"><i/><i/><i/> Searching verified records</div>}</div>
   {messages.length===1&&<div className="suggestions">{suggestions.map((s,i)=><button key={s} onClick={()=>send(s)}><span>{i===0?<Link2/>:i===1?<BarChart3/>:<Languages/>}</span>{s}<ChevronRight/></button>)}</div>}
   <div className="composer"><div className="input"><textarea value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}}} placeholder={lang==='EN'?'Ask a question about crime records…':'ಅಪರಾಧ ದಾಖಲೆಗಳ ಬಗ್ಗೆ ಪ್ರಶ್ನಿಸಿ…'}/><button className="mic" title="Voice input"><Mic/></button><button className="send" onClick={()=>send()} disabled={!input.trim()||loading}><Send/></button></div><p><ShieldCheck/> Responses cite retrieved FIR records. Verify operational decisions independently.</p></div>
  </section>:<DashboardView data={dash}/>}</main>
  {audit&&<div className="modal-bg" onClick={()=>setAudit(null)}><div className="modal" onClick={e=>e.stopPropagation()}><div className="modal-head"><div><span className="eyebrow">Evidence trail</span><h2>Why this answer?</h2></div><button onClick={()=>setAudit(null)}>×</button></div>{audit.map(x=><div className="audit-row" key={x.id}><span className={x.verified?'verified':''}><BadgeCheck/> {x.verified?'Verified':'Failed'}</span><b>{x.query}</b><small>{x.record_ids.length} records · {x.entry_hash.slice(0,18)}…</small></div>)}</div></div>}
 </div>
}

function DashboardView({data}:{data:Dashboard|null}){return <section className="dashboard"><div className="fairness"><ShieldCheck/><div><b>Ethical analytics by design</b><span>{data?.fairness_note||'PRAHARI displays area aggregates only — never individual risk scores.'}</span></div></div><div className="stats"><article><span>Visible records</span><strong>{data?.total_visible||'—'}</strong><small>Within current jurisdiction</small></article><article><span>Active districts</span><strong>{data?.by_district.length||'—'}</strong><small>Aggregated case coverage</small></article><article><span>Audit integrity</span><strong>100%</strong><small>Verified interaction chain</small></article></div><div className="dash-grid"><div className="panel"><div className="panel-title"><div><span className="eyebrow">Area-level distribution</span><h2>Cases by district</h2></div><MapPin/></div><div className="bars">{data?.by_district.slice(0,8).map((d,i)=><div className="bar-row" key={d.district}><span>{d.district}</span><div><i style={{width:`${Math.max(16,d.count/Math.max(...data.by_district.map(x=>x.count))*100)}%`}}/></div><b>{d.count}</b></div>)}</div></div><div className="panel"><div className="panel-title"><div><span className="eyebrow">Latest intelligence</span><h2>Recent FIRs</h2></div><FileSearch/></div>{data?.recent.map(r=><div className="recent" key={r.id}><span>{r.id.slice(-4)}</span><div><b>{r.fir_number}</b><small>{r.station} · {r.district}</small></div><em>{r.status}</em></div>)}</div></div></section>}
export default App

