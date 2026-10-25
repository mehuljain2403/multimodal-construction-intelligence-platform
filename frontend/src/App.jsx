import { useState } from 'react';
import {
  Activity,
  ShieldCheck,
  ScanLine,
  House,
  ClipboardList,
  CloudSun,
  BookOpen,
  Upload,
  Send,
  HardHat,
  Menu,
  Code2,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';

const MODES = [
  {id:'safety', label:'Site safety', icon:ShieldCheck, desc:'Hazards, PPE, housekeeping and corrective actions'},
  {id:'crack', label:'Crack analysis', icon:ScanLine, desc:'Document visible cracks and identify escalation steps'},
  {id:'valuation', label:'Real-estate valuation', icon:House, desc:'Illustrative estimate from area and rate assumptions'},
  {id:'planning', label:'Project planning', icon:ClipboardList, desc:'Sequencing, dependencies, materials and risks'},
  {id:'daily_assistant', label:'Daily site assistant', icon:CloudSun, desc:'Daily brief, weather caveats and coordination'},
  {id:'knowledge', label:'Construction Q&A', icon:BookOpen, desc:'Ask a construction or project delivery question'},
];
const DEFAULT_PROMPTS = {
 safety:'Review the site for hazards and suggest practical mitigations.',
 crack:'Describe the visible crack and suggest documentation and escalation steps.',
 valuation:'Estimate an illustrative property value using the details provided.',
 planning:'Create a preliminary construction execution plan with key dependencies.',
 daily_assistant:'Prepare a daily site briefing and list today’s checks.',
 knowledge:'Explain the difference between a BOQ and an estimate.'
};
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function App() {
  const [mode,setMode] = useState('safety');
  const [prompt,setPrompt] = useState(DEFAULT_PROMPTS.safety);
  const [area,setArea] = useState('1200');
  const [rate,setRate] = useState('3500');
  const [location,setLocation] = useState('');
  const [image,setImage] = useState(null);
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState('');
  const [result,setResult] = useState(null);
  const [navOpen,setNavOpen] = useState(false);

  const chooseMode = id => { setMode(id); setPrompt(DEFAULT_PROMPTS[id]); setResult(null); setError(''); };
  async function submit(e) {
    e.preventDefault(); setBusy(true); setError(''); setResult(null);
    const fd = new FormData();
    fd.append('mode',mode); fd.append('prompt',prompt);
    const data = {};
    if (mode === 'valuation') {
      if (area) data.area_sqft = Number(area);
      if (rate) data.rate_per_sqft = Number(rate);
      data.location = location;
    } else if (location) data.location = location;
    fd.append('project_data',JSON.stringify(data));
    if (image) fd.append('image',image);
    try {
      const res = await fetch(`${API}/api/analyze`,{method:'POST',body:fd});
      const body = await res.json();
      if (!res.ok) throw new Error(body.detail || 'Analysis failed. Please try again.');
      setResult(body);
    } catch(err) {
      setError(`${err.message}. Check that the FastAPI backend is running at ${API}.`);
    } finally { setBusy(false); }
  }
  const active = MODES.find(m=>m.id===mode);
  return <div className="app-shell">
    <aside className={`sidebar ${navOpen?'open':''}`}>
      <div className="brand"><div className="brand-icon"><HardHat size={22}/></div><div><b>BuildSense</b><span>CONSTRUCTION INTELLIGENCE</span></div></div>
      <div className="workspace-label">WORKSPACE</div>
      <div className="project-chip"><div className="project-mark">MC</div><div><b>Multimodal CI Platform</b><small>Individual project</small></div><span className="live-dot"/></div>
      <div className="nav-label">INTELLIGENCE TOOLS</div>
      {MODES.map(m=>{const Icon=m.icon;return <button key={m.id} className={`nav-item ${mode===m.id?'selected':''}`} onClick={()=>{chooseMode(m.id);setNavOpen(false)}}><Icon size={18}/><span>{m.label}</span>{mode===m.id&&<span className="nav-active"/>}</button>})}
      <div className="sidebar-bottom"><div className="secure-card"><div className="secure-icon"><ShieldCheck size={17}/></div><div><b>Safety-first AI</b><p>AI insights support expert review, never replace it.</p></div></div><div className="user-row"><div className="avatar">MC</div><div><b>Project workspace</b><small>Prototype environment</small></div><span className="dots">•••</span></div></div>
    </aside>
    <main className="main">
      <header className="topbar"><button className="menu-btn" onClick={()=>setNavOpen(!navOpen)}><Menu size={20}/></button><div className="breadcrumbs">Workspace <span>/</span> <b>{active.label}</b></div><div className="top-right"><span className="status"><i/> Prototype</span><a
  className="icon-link"
  href="https://github.com/"
  target="_blank"
  rel="noreferrer"
  aria-label="GitHub"
>
  <Code2 size={17} />
</a></div></header>
      <section className="hero"><div className="hero-copy"><div className="eyebrow"><span className="eyebrow-icon"><Activity size={14}/></span> MULTIMODAL CONSTRUCTION INTELLIGENCE</div><h1>Make better site decisions.<br/><em>Build with confidence.</em></h1><p>Bring construction descriptions, site imagery, and project data together to generate actionable insights for safer, smarter project delivery.</p><div className="hero-tags"><span><CheckCircle2 size={14}/> Text + image input</span><span><CheckCircle2 size={14}/> Structured AI output</span><span><CheckCircle2 size={14}/> Six specialist workflows</span></div></div><div className="hero-art"><div className="art-orbit orbit-one"/><div className="art-orbit orbit-two"/><div className="blueprint"><div className="bp-top"><span>FIELD INTELLIGENCE</span><span className="bp-dot"/></div><div className="bp-building"><div className="bp-roof"/><div className="bp-floor f1"/><div className="bp-floor f2"/><div className="bp-floor f3"/><div className="bp-base"/></div><div className="bp-bottom"><span>ANALYZE</span><span>ASSESS</span><span>ACT</span></div></div><div className="floating-badge"><ShieldCheck size={17}/><span><b>Safety aware</b><small>Decision support</small></span></div></div></section>
      <section className="stats"><div className="stat"><div className="stat-icon purple"><Activity size={18}/></div><div><span>AI WORKFLOWS</span><b>06 <small>available</small></b></div></div><div className="stat"><div className="stat-icon green"><ShieldCheck size={18}/></div><div><span>OUTPUT FORMAT</span><b>Structured <small>JSON</small></b></div></div><div className="stat"><div className="stat-icon amber"><ScanLine size={18}/></div><div><span>INPUT TYPES</span><b>Multimodal <small>text + image</small></b></div></div><div className="stat"><div className="stat-icon blue"><CheckCircle2 size={18}/></div><div><span>ENVIRONMENT</span><b>Demo ready <small>local</small></b></div></div></section>
      <section className="work-area"><div className="section-heading"><div><div className="section-kicker">WORKBENCH</div><h2>What would you like to assess?</h2><p>Select a workflow, provide the available context, and run an analysis.</p></div><div className="api-pill"><span/> API-connected</div></div>
        <div className="mode-grid">{MODES.map(m=>{const Icon=m.icon;return <button key={m.id} className={`mode-card ${mode===m.id?'active':''}`} onClick={()=>chooseMode(m.id)}><div className="mode-icon"><Icon size={19}/></div><div className="mode-text"><b>{m.label}</b><span>{m.desc}</span></div><span className="card-arrow">↗</span></button>})}</div>
        <div className="analysis-layout"><form className="input-card" onSubmit={submit}><div className="card-title"><div><span className="section-kicker">01 / INPUT</span><h3>{active.label}</h3></div><span className="required-tag">● Ready to configure</span></div><label htmlFor="prompt">Describe your project or question <span>*</span></label><textarea id="prompt" value={prompt} onChange={e=>setPrompt(e.target.value)} required maxLength={12000} placeholder="Describe what you see, what you need to know, and any relevant context…"/><div className="field-meta"><span>Specific details improve the quality of guidance.</span><span>{prompt.length}/12,000</span></div>
          {mode==='valuation'&&<div className="field-grid"><div><label htmlFor="area">Built-up area (sq ft)</label><input
  id="area"
  type="number"
  min="1"
  value={area}
  onChange={e => setArea(e.target.value)}
/></div><div><label htmlFor="rate">Rate per sq ft (₹)</label><input
  id="rate"
  type="number"
  min="1"
  value={rate}
  onChange={e => setRate(e.target.value)}
/></div></div>}
          <div className="field-block"><label htmlFor="location">Project location / context <small>OPTIONAL</small></label><input id="location" value={location} onChange={e=>setLocation(e.target.value)} placeholder="e.g. Bhopal, residential G+2 building"/></div>
          <label className="upload-label">Site image <small>OPTIONAL · JPG, PNG, WEBP</small></label><label className={`upload-zone ${image?'has-file':''}`} htmlFor="image"><div className="upload-icon"><Upload size={20}/></div><div><b>{image?image.name:'Drop an image here or browse'}</b><span>{image?`${(image.size/1024/1024).toFixed(2)} MB selected`:'One image · max 8 MB · clear site photos work best'}</span></div><span className="browse-btn">Browse files</span><input id="image" type="file" accept="image/png,image/jpeg,image/webp,image/gif" onChange={e=>setImage(e.target.files?.[0]||null)}/></label>
          {image&&<button type="button" className="remove-file" onClick={()=>setImage(null)}>Remove selected image</button>}
          <div className="form-footer"><div className="privacy-note"><ShieldCheck size={16}/><span>Image is sent to your configured backend for analysis.</span></div><button className="submit-btn" disabled={busy||!prompt.trim()}>{busy?<><span className="spinner"/> Analyzing…</>:<>Run analysis <Send size={16}/></>}</button></div>
        </form>
        <div className="result-card"><div className="result-header"><div><span className="section-kicker">02 / RESULTS</span><h3>Intelligence report</h3></div><span className="result-indicator"><i/>{result?'Complete':'Awaiting input'}</span></div>
          {!result&&!busy&&!error&&<div className="empty-state"><div className="empty-illustration"><div className="empty-ring"><ScanLine size={29}/></div><span className="spark spark-a">✦</span><span className="spark spark-b">✧</span></div><h4>Your report starts here</h4><p>Run an analysis to see a structured summary, findings, recommendations, and any available estimate.</p><div className="empty-checks"><span><CheckCircle2 size={15}/> Clear findings</span><span><CheckCircle2 size={15}/> Actionable next steps</span><span><CheckCircle2 size={15}/> Limitations included</span></div></div>}
          {busy&&<div className="loading-state"><div className="loading-ring"/><h4>Reviewing your input…</h4><p>Preparing a structured construction intelligence report.</p></div>}
          {error&&<div className="error-box"><AlertTriangle size={22}/><div><b>Couldn’t complete analysis</b><p>{error}</p></div></div>}
          {result&&<div className="report"><div className="report-summary"><span className="summary-label">SUMMARY</span><p>{result.summary}</p><span className={`source-badge ${result.source}`}>{result.source==='ai'?'AI-generated':'Demo mode'}</span></div>
            {result.estimate&&<div className="estimate-box"><span>ILLUSTRATIVE ESTIMATE · {result.estimate.currency}</span><b>{result.estimate.low!=null?`${Number(result.estimate.low).toLocaleString()} – ${Number(result.estimate.high).toLocaleString()}`:'Not enough data'}</b>{result.estimate.assumptions?.map((a,i)=><small key={i}>• {a}</small>)}</div>}
            {result.findings?.length>0&&<div className="report-section"><h4>Findings</h4>{result.findings.map((f,i)=><div className="finding" key={i}><div className={`severity ${f.severity}`}>{f.severity}</div><b>{f.title}</b><p>{f.description}</p><div className="recommendation"><strong>Recommended action:</strong> {f.recommendation}</div></div>)}</div>}
            {result.recommendations?.length>0&&<div className="report-section"><h4>Recommended next steps</h4><ol>{result.recommendations.map((r,i)=><li key={i}>{r}</li>)}</ol></div>}
            {result.limitations?.length>0&&<div className="limitations"><AlertTriangle size={15}/><div><b>Important limitations</b>{result.limitations.map((l,i)=><p key={i}>{l}</p>)}</div></div>}
            <details className="json-details"><summary>View structured JSON</summary><pre>{JSON.stringify(result,null,2)}</pre></details>
          </div>}
        </div></div>
      </section>
      <footer><span>BuildSense <b>·</b> Multimodal Construction Intelligence</span><span>Built for responsible decision support <ShieldCheck size={14}/></span></footer>
    </main>
  </div>
}
