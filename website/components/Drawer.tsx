'use client';

import { useEffect, useRef, useState } from 'react';
import { useCockpit } from '@/lib/context';
import { LABEL } from '@/lib/stages.mjs';
import { briefBullets } from '@/lib/job-brief.mjs';
import { ago, headlineText, jobDetails, jobFlags } from '@/lib/job-facts.mjs';
import { nextStep, replyDrafts } from '@/lib/next-step.mjs';
import { parseApplication } from '@/lib/application-review.mjs';
import { plainText } from '@/lib/plain-text.mjs';
import { artifactUrl, artifactVersion, useArtifactText } from '@/lib/artifact-content.mjs';
import CopyButton from './CopyButton';
import NewMessage from './NewMessage';
import LeadActions from './LeadActions';
import { analyticsMemberText } from '@/lib/analytics-contract';
import { CallCard } from './AnalyticsPage';
import './drawer.css';

// Shown in their own sections; every other file is a plain link. The pitch page has no
// section of its own any more (12.10.2026) and stays off the file list too.
const SHOWN = new Set(['pitch.html', 'application.md', 'call-prep.md', 'call-prep.html', 'proposal.md']);

export default function Drawer() {
  const { state, api, toast, drawerId, closeDrawer } = useCockpit();
  const [job, setJob] = useState<any>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (drawerId) requestAnimationFrame(() => closeRef.current?.focus());
  }, [drawerId]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => { if (event.key === 'Escape' && drawerId) closeDrawer(); };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [drawerId, closeDrawer]);

  useEffect(() => {
    document.body.classList.toggle('drawer-open', !!drawerId);
    return () => document.body.classList.remove('drawer-open');
  }, [drawerId]);

  useEffect(() => {
    if (!drawerId) { setJob(null); return; }
    setJob((current: any) => current?.id === drawerId ? current : null);
    let cancelled = false;
    void api(`/api/job/${drawerId}`).then(result => {
      if (cancelled) return;
      if (!result.ok) { toast('Could not load that job.'); closeDrawer(); return; }
      setJob(result.data);
    });
    return () => { cancelled = true; };
  }, [api, closeDrawer, drawerId, state?.generated_at, toast]);

  const step = job ? nextStep(job) : null;
  // The brief sits at the top while the call is still ahead, and with the proposal after it.
  const prep = (job?.artifacts || []).includes('call-prep.md') ? <CallPrep job={job} /> : null;
  const callAhead = job?.status === 'replied' || job?.status === 'call';
  return <aside className={`drawer${drawerId ? ' open' : ''}`} aria-labelledby={drawerId ? 'drawer-title' : undefined}
    aria-hidden={!drawerId} inert={!drawerId} aria-busy={!!drawerId && !job}>
    {drawerId ? <>
      <div className="drawer-head">
        <div className="drawer-title">
          <h3 id="drawer-title">{!job ? 'Loading job' : job.url
            ? <a href={job.url} target="_blank" rel="noopener" title="Open on Upwork">{job.title}</a> : job.title}</h3>
          <button ref={closeRef} className="drawer-close" onClick={closeDrawer} aria-label="Close">✕</button>
        </div>
        {job ? <p className="drawer-headline">{headlineText(job)}</p> : null}
        {job ? <div className="drawer-stage"><span className={`stage-label stage-${job.status}`}>{LABEL[job.status] || job.status}</span></div> : null}
      </div>
      <div className="drawer-body">{job ? <>
        {step && (step.detail || step.extras.length) ? <section className="drawer-section" aria-label="Next step">
          <h4>Next step</h4>
          <NewMessage job={job} />
          {step.detail ? <p>{step.detail}</p> : null}
          {step.command ? <CopyButton text={step.command} label={step.command} /> : null}
          <LeadActions job={job} labels />
          {step.extras.length ? <p className="drawer-extras">{step.extras.map((command: string) =>
            <CopyButton key={command} compact text={command} label={command.split(' ')[0]} />)}</p> : null}
        </section> : null}
        {callAhead ? prep : null}
        <Conversation job={job} />
        <ProposalContext job={job} />
        {Array.isArray(job.call_cards) && job.call_cards.length > 0 ? <section className="drawer-section" aria-label="Saved call reviews"><h4>Saved call reviews</h4>{job.call_cards.map((card: any, index: number) => <CallCard key={index} card={card} />)}</section> : null}
        <TheJob job={job} />
        <WorthIt job={job} />
        {(job.artifacts || []).includes('application.md') ? <Application job={job} /> : null}
        {callAhead ? null : prep}
        {(job.artifacts || []).includes('proposal.md') ? <Proposal job={job} /> : null}
        <Drafts job={job} />
        <OtherFiles job={job} />
      </> : <p className="empty">Loading job.</p>}</div>
    </> : null}
  </aside>;
}

function SavedContext({ value }: { value: any }) {
  if (value == null) return <>Unknown</>;
  if (Array.isArray(value)) return <ul>{value.map((item, index) => <li key={index}><SavedContext value={item} /></li>)}</ul>;
  if (typeof value === 'object') return <dl>{Object.entries(value).map(([key, item]) => <div key={key}><dt>{analyticsMemberText(key)}</dt><dd><SavedContext value={item} /></dd></div>)}</dl>;
  return <>{typeof value === 'boolean' ? value ? 'Yes' : 'No' : analyticsMemberText(value)}</>;
}

function ProposalContext({ job }: { job: any }) {
  const context = job.lead_context || {}, viewed = context.proposal_viewed ?? job.proposal_viewed;
  const insights = context.proposal_insights ?? job.proposal_insights;
  if (viewed == null && insights == null && !context.week) return null;
  const flag = typeof viewed === 'object' ? viewed?.value : viewed;
  return <section className="drawer-section" aria-label="Proposal observation context">
    <h4>Proposal observation context</h4>
    <p>Viewed flag: {flag === true ? 'Observed viewed' : flag === false ? 'Observed not viewed' : 'Unknown · no observation saved'}</p>
    {viewed?.observed_at || context.proposal_viewed_at ? <p>Observed at {viewed?.observed_at || context.proposal_viewed_at}. This is an observation time; the actual view time is unknown.</p> : null}
    <p>This context is separate from performance KPIs.</p>
    {insights ? <><h5>Post-submission proposal insights</h5><SavedContext value={insights.data ?? insights} />{insights.fetched_at ? <p>Read at {insights.fetched_at} · {insights.source || 'Source not recorded'}</p> : null}</> : <p>Post-submission proposal insights were not saved.</p>}
  </section>;
}

/** What the client asked for, in bullets of fifty words at most (12.10.2026).
 *
 * The drawer answers one question, do I apply. An outcome paragraph, key work and must-haves
 * came to as many words as the posting itself and saved nobody time. The headline above says
 * who wants what; these bullets add the work and the hard must-haves, and anyone who wants
 * the client's own words reads the posting on Upwork.
 */
function TheJob({ job }: { job: any }) {
  const bullets = briefBullets(job);
  return <section className="drawer-section">
    <h4>The job</h4>
    {bullets.length ? <ul className="drawer-list">{bullets.map((item: string) => <li key={item}>{item}</li>)}</ul>
      : <p className="muted">No summary saved for this job.</p>}
    {job.url ? <p className="drawer-note"><a href={job.url} target="_blank" rel="noopener">Read the full post on Upwork</a></p> : null}
  </section>;
}

/** The facts that decide whether the job is worth an application. */
// Score, fit, Connects and competition answer one question: is this worth applying to.
// The drawer showed them at every stage, so a won client still carried the case for
// spending Connects on him, which is a decision nobody can take again.
const DECIDING = new Set(['new']);

function WorthIt({ job }: { job: any }) {
  const rows = jobDetails(job), flags = jobFlags(job);
  if (!DECIDING.has(job.status) || (!rows.length && !flags.length)) return null;
  return <section className="drawer-section">
    <h4>Worth it?</h4>
    {flags.length ? <p className="drawer-flags">{flags.map(flag => <span key={flag.text} className={`uw-flag ${flag.tone}`}>{flag.text}</span>)}</p> : null}
    <dl className="drawer-facts">{rows.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
  </section>;
}

function Application({ job }: { job: any }) {
  const content = useArtifactText(job.id, 'application.md', artifactVersion(job.files, 'application.md'));
  if (content.status === 'loading') return <section className="drawer-section"><h4>Cover letter</h4><p className="empty">Loading.</p></section>;
  if (content.status !== 'ready') return <section className="drawer-section"><h4>Cover letter</h4>
    <p className="empty">The application could not be read. <a href={artifactUrl(job.id, 'application.md')} target="_blank" rel="noopener">Open the file</a>.</p></section>;
  const { coverLetter, answers } = parseApplication(content.text);
  return <section className="drawer-section">
    <h4>Cover letter</h4>
    <pre className="drawer-text">{coverLetter}</pre>
    <CopyButton text={coverLetter} label="Copy cover letter" />
    {answers.map((item: any, index: number) => <div key={index} className="drawer-answer">
      <h5>{item.question}</h5>
      <pre className="drawer-text">{item.answer}</pre>
      <CopyButton text={item.answer} label="Copy answer" />
    </div>)}
  </section>;
}

/** The member's own page for the call. It is read, never sent, so it has no copy button.
 * Every fact in the file carries its link; the panel shows the brief without them and the
 * source list, and the file itself is one click away. */
function CallPrep({ job }: { job: any }) {
  const content = useArtifactText(job.id, 'call-prep.md', artifactVersion(job.files, 'call-prep.md'));
  if (content.status === 'loading') return <section className="drawer-section"><h4>Call prep</h4><p className="empty">Loading.</p></section>;
  if (content.status !== 'ready') return <section className="drawer-section"><h4>Call prep</h4>
    <p className="empty">The call prep could not be read. <a href={artifactUrl(job.id, 'call-prep.md')} target="_blank" rel="noopener">Open the file</a>.</p></section>;
  const brief = plainText(content.text.split(/^## Sources[ \t]*$/m)[0].replace(/[ \t]*\(\[[^\]]*\]\([^)]*\)\)/g, ''));
  return <section className="drawer-section">
    <h4>Call prep</h4>
    <pre className="drawer-text">{brief}</pre>
    <p className="drawer-note">{(job.artifacts || []).includes('call-prep.html')
      ? <a href={artifactUrl(job.id, 'call-prep.html')} target="_blank" rel="noopener">Open the call prep page</a>
      : <a href={artifactUrl(job.id, 'call-prep.md')} target="_blank" rel="noopener">Open the brief with its sources</a>}</p>
  </section>;
}

function Proposal({ job }: { job: any }) {
  const content = useArtifactText(job.id, 'proposal.md', artifactVersion(job.files, 'proposal.md'));
  if (content.status === 'loading') return <section className="drawer-section"><h4>Proposal</h4><p className="empty">Loading.</p></section>;
  if (content.status !== 'ready') return <section className="drawer-section"><h4>Proposal</h4>
    <p className="empty">The proposal could not be read. <a href={artifactUrl(job.id, 'proposal.md')} target="_blank" rel="noopener">Open the file</a>.</p></section>;
  return <section className="drawer-section">
    <h4>Proposal</h4>
    <pre className="drawer-text">{plainText(content.text)}</pre>
    <CopyButton text={plainText(content.text)} label="Copy proposal" />
  </section>;
}

// The client's own words, which this surface has never shown: sync saves every thread
// "for the cockpit's chat window" and there was no chat window, so a member with fifteen
// live conversations read the job posting in three sections and the client in none.
function Conversation({ job }: { job: any }) {
  const thread = job.thread || {};
  const all: any[] = Array.isArray(thread.messages) ? thread.messages : [];
  if (!all.length) {
    // A missing thread is a fact worth stating: prune follows KEEP_CHAT_HOURS (90 days by default) and only a
    // /dashboard run brings it back, so silence here would read as a client who said nothing.
    return <section className="drawer-section" aria-label="Conversation">
      <h4>Conversation</h4>
      <p className="muted">No saved messages. Run /dashboard to pull the thread again.</p>
    </section>;
  }
  const shown = all.slice(-8);
  return <section className="drawer-section" aria-label="Conversation">
    <h4>Conversation{all.length > shown.length ? ` · last ${shown.length} of ${all.length}` : ''}</h4>
    <ol className="thread">
      {shown.map((m, index) => <li key={m.id || index} className={`msg ${m.from}`}>
        <span className="msg-who">{m.from === 'me' ? 'You' : m.from === 'system' ? 'Upwork' : (m.name || 'Client')}
          {m.at ? <span className="msg-at">{ago(m.at)}</span> : null}</span>
        <p className="msg-text">{m.text}</p>
      </li>)}
    </ol>
  </section>;
}

function Drafts({ job }: { job: any }) {
  const drafts = replyDrafts(job);
  if (!drafts.length) return null;
  return <section className="drawer-section">
    <h4>Reply drafts</h4>
    {drafts.map((draft, index) => <div key={index} className="drawer-answer">
      <h5>{draft.label}</h5>
      <pre className="drawer-text">{draft.text}</pre>
      <CopyButton text={draft.text} label="Copy draft" />
    </div>)}
  </section>;
}

const GROUPS: [string, string][] = [
  ['client', 'The client sees'],
  ['send', 'You send'],
  ['asset', 'Material'],
  ['data', 'Records'],
];

function OtherFiles({ job }: { job: any }) {
  const files = (job.files || []).filter((file: any) => !SHOWN.has(file.name));
  if (!files.length) return null;
  return <>{GROUPS.map(([key, title]) => {
    const group = files.filter((file: any) => (file.role || 'data') === key);
    if (!group.length) return null;
    return <section className="drawer-section" key={key}>
      <h4>{title}</h4>
      <ul className="drawer-files">{group.map((file: any) => <li key={file.name}>
        <a href={artifactUrl(job.id, file.name, file.version)} target="_blank" rel="noopener">{file.name}</a>
      </li>)}</ul>
    </section>;
  })}</>;
}
