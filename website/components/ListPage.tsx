'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useCockpit } from '@/lib/context';
import { ANALYTICS_LEADS_PARAM, analyticsLeadIds } from '@/lib/analytics-navigation';
import { BOARD, LABEL, LIST } from '@/lib/stages.mjs';
import { cardCommands, nextStep, waitingState } from '@/lib/next-step.mjs';
import { daysInStage, searchJobs, sortJobs } from '@/lib/list-view.mjs';
import {
  bidsTone, budgetText, budgetTone, clientLines, clientTone, competitionLines, headlineText, jobFlags, postedTone, scoreTone,
} from '@/lib/job-facts.mjs';
import CopyButton from './CopyButton';
import NewMessage from './NewMessage';
import FilterMenu from './FilterMenu';
import LeadActions from './LeadActions';

type Layout = 'list' | 'board';
// The list shows one pile at a time: what is still to send, or what went out.
type Pile = 'unsent' | 'sent';
type SortKey = 'score' | 'job' | 'client' | 'competition' | 'budget' | 'step';
type Sort = { key: SortKey; desc: boolean } | null;

const LAYOUT_KEY = 'cockpit-layout';
// How fresh a posting is, in hours. A dense search term turns over ten postings in
// two hours, so "today" is not a useful bucket and these are.
const FRESH: [number, string][] = [[0, 'Any age'], [4, '4h'], [6, '6h'], [12, '12h'], [24, '24h']];
// The list holds the leads still to decide on; everything from Applied on lives on the board.
// The title column is gone (27.09.2026): an Upwork title is the client's own SEO line
// and says the same thing forty times over, while the summary is the sentence that
// actually decides. The title survives as the link's tooltip.
// The last column holds the check and the X on their own (12.10.2026): beside the command
// chip they read as stray marks, and the summary gives up the width for them.
const COLUMNS: { key: SortKey | 'summary' | 'done'; label: string; width?: number }[] = [
  { key: 'score', label: 'Score', width: 72 },
  { key: 'summary', label: 'Summary' },
  { key: 'client', label: 'Client', width: 200 },
  { key: 'competition', label: 'Competition', width: 158 },
  { key: 'budget', label: 'Budget', width: 128 },
  { key: 'step', label: 'Next step', width: 204 },
  { key: 'done', label: 'Sent?', width: 104 },
];

export default function ListPage() {
  const { state, drawerId, openDrawer, closeDrawer } = useCockpit();
  const router = useRouter();
  const searchParams = useSearchParams();
  const selectedIds = useMemo(() => analyticsLeadIds(searchParams.get(ANALYTICS_LEADS_PARAM)), [searchParams]);
  const fromAnalytics = selectedIds !== null;
  const [layout, setLayout] = useState<Layout>('list');
  const [query, setQuery] = useState('');
  const [sort, setSort] = useState<Sort>(null);

  useEffect(() => {
    try { if (localStorage.getItem(LAYOUT_KEY) === 'board') setLayout('board'); } catch { /* Storage is optional. */ }
  }, []);

  // Longest waiting first by default: a board exists to show what is going stale.
  const [oldestFirst, setOldestFirst] = useState(true);
  const [dueOnly, setDueOnly] = useState(false);
  const [pile, setPile] = useState<Pile>('unsent');
  // Hours: 0 shows everything.
  const [fresh, setFresh] = useState(0);
  const all: any[] = state?.jobs || [];
  const listed = useMemo(() => all.filter(j => LIST.includes(j.status)), [all]);
  const unsent = useMemo(() => listed.filter(j => j.status === 'new'), [listed]);
  const pool = useMemo(() => fromAnalytics ? all.filter(j => selectedIds.includes(String(j.id)))
    : layout === 'board' ? all.filter(j => BOARD.includes(j.status))
    : pile === 'sent' ? listed.filter(j => j.status !== 'new') : unsent,
    [all, layout, listed, pile, unsent, fromAnalytics, selectedIds]);
  // On the board: a reply or a follow-up is due from the member now, not set for later.
  const byDue = useMemo(() => dueOnly && layout === 'board' && !fromAnalytics ? pool.filter(j => waitingState(j).kind === 'act') : pool,
    [pool, dueOnly, layout, fromAnalytics]);
  // A posting stops being worth Connects within hours, so freshness is a filter and
  // not only a colour. Anything without a posting date stays visible: a missing field
  // is not evidence that the job is old.
  const filtered = useMemo(() => {
    // Only on what is still to send. On the board a "posted 3 days ago" lead is a live
    // conversation, and a sent application is already in flight: hiding either behind an
    // apply-time filter loses work.
    if (fromAnalytics || !fresh || layout === 'board' || pile === 'sent') return byDue;
    const cutoff = Date.now() - fresh * 3600e3;
    return byDue.filter(j => !j.posted_date || Date.parse(j.posted_date) >= cutoff);
  }, [byDue, fresh, layout, pile, fromAnalytics]);
  const jobs = useMemo(() => sortJobs(fromAnalytics ? filtered : searchJobs(filtered, query), layout === 'board' && !fromAnalytics ? null : sort),
    [filtered, query, sort, layout, fromAnalytics]);
  if (!state) return null;

  const choose = (next: Layout) => {
    setLayout(next);
    try { localStorage.setItem(LAYOUT_KEY, next); } catch { /* Storage is optional. */ }
  };
  const toggle = (id: string) => { if (!fromAnalytics) drawerId === id ? closeDrawer() : openDrawer(id); };
  // Up, down, then back to the default order.
  const sortBy = (key: SortKey) => setSort(current => current?.key !== key ? { key, desc: false } : current.desc ? null : { key, desc: true });
  const noun = layout === 'board' ? 'in the pipeline' : pile === 'sent' ? 'sent' : 'to decide on';
  const dueTotal = pool.filter(j => waitingState(j).kind === 'act').length;

  return <div>
    {fromAnalytics ? <div className="toolbar" data-analytics-leads>
      <button type="button" onClick={() => router.back()}>← Back to Analytics</button>
      <span className="count" aria-live="polite">{pool.length} selected {pool.length === 1 ? 'lead' : 'leads'}</span>
      {pool.length < selectedIds.length ? <span>{selectedIds.length - pool.length} selected leads are no longer saved.</span> : null}
    </div> : <>
    <div className="toolbar">
      <div className="seg" role="group" aria-label="Layout" style={{ '--segment-index': Number(layout === 'board') } as React.CSSProperties}>
        <button onClick={() => choose('list')} aria-pressed={layout === 'list'}>List</button>
        <button onClick={() => choose('board')} aria-pressed={layout === 'board'}>Board</button>
      </div>
      {layout === 'board' ? <div className="seg" role="group" aria-label="Order"
        style={{ '--segment-index': Number(!oldestFirst) } as React.CSSProperties}>
        <button onClick={() => setOldestFirst(true)} aria-pressed={oldestFirst}>Longest waiting</button>
        <button onClick={() => setOldestFirst(false)} aria-pressed={!oldestFirst}>Newest</button>
      </div> : null}
      <label className="search-box">
        <input type="search" placeholder="Search jobs" aria-label="Search" value={query} onChange={e => setQuery(e.target.value)} />
      </label>
      {layout === 'board' ? <button type="button" className={`due-toggle with-icon${dueOnly ? ' on' : ''}`} aria-pressed={dueOnly}
        title="Only the conversations where a reply or a follow-up is due from you" onClick={() => setDueOnly(v => !v)}>
        <svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M6.5 4L3 7.5 6.5 11M3.5 7.5h6a3.5 3.5 0 0 1 3.5 3.5v1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
        {dueTotal ? `My turn · ${dueTotal}` : 'My turn'}</button>
        : <div className="seg with-icons" role="group" aria-label="Sent or unsent" style={{ '--segment-index': Number(pile === 'sent') } as React.CSSProperties}>
          <button onClick={() => setPile('unsent')} aria-pressed={pile === 'unsent'}>
            <svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><circle cx="8" cy="8" r="5" stroke="currentColor" strokeWidth="1.5" /></svg>Unsent</button>
          <button onClick={() => setPile('sent')} aria-pressed={pile === 'sent'}>
            <svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3.5 8.5l3 3 6-7" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" /></svg>Sent</button>
        </div>}
      {layout === 'board' ? null : <FilterMenu />}
      {layout === 'board' || pile === 'sent' ? null : <div className="seg wide" role="group" aria-label="Posted within"
        style={{ '--segment-index': FRESH.findIndex(([h]) => h === fresh),
                 '--segment-count': FRESH.length } as React.CSSProperties}>
        {FRESH.map(([hours, label]) => <button key={label} onClick={() => setFresh(hours)}
          aria-pressed={fresh === hours}>{label}</button>)}
      </div>}
      <span className="count" aria-live="polite">{jobs.length === pool.length ? `${pool.length} ${noun}` : `${jobs.length} of ${pool.length} ${noun}`}</span>
    </div>
    </>}
    {fromAnalytics ? jobs.length ? <Table jobs={jobs} sort={sort} sortBy={sortBy} drawerId={null} toggle={toggle} readOnly />
      : <p className="empty">No saved leads match this evidence.</p>
      : layout === 'board' ? <Board jobs={jobs} oldestFirst={oldestFirst} drawerId={drawerId} toggle={toggle} />
      : !pool.length ? <p className="empty">{pile === 'sent'
        ? 'Nothing sent yet. Tick the check on a job once you have applied on Upwork.'
        : 'No new jobs. Run /find-jobs in Claude Code.'}</p>
        : !jobs.length ? <p className="empty">{query.trim()
          ? `Nothing matches “${query}”.`
          : fresh ? `Nothing posted in the last ${fresh} hours. Pick a longer window or Any age.`
            : 'Nothing matches these filters. Turn one off to see your leads.'}</p>
          : <Table jobs={jobs} sort={sort} sortBy={sortBy} drawerId={drawerId} toggle={toggle} />}
  </div>;
}

// Green, amber and red for the facts that decide whether a lead is worth it.
const tone = (value: string) => value ? `tone-${value}` : '';

function StepCell({ job }: { job: any }) {
  const step = nextStep(job);
  const state = waitingState(job);
  return <>
    <span className="step-row">
      {step.command
        ? <CopyButton compact text={step.command} label={step.command.split(' ')[0]} />
        : <span className="step-hint">{step.label || '–'}</span>}
      <OnUpwork job={job} />
    </span>
    <span className={`uw-sub state-${state.kind.replace(' ', '-')}${state.late ? ' tone-bad' : ''}`}>
      {/* The chip already says what to do, so the line under it says only how long
          this has been sitting. Without a chip it carries the state itself. */}
      {state.kind === 'act' && !state.late
        ? `${state.age} in stage`
        : state.detail}
    </span>
  </>;
}

function Table({ jobs, sort, sortBy, drawerId, toggle, readOnly = false }: {
  jobs: any[]; sort: Sort; sortBy: (key: SortKey) => void; drawerId: string | null; toggle: (id: string) => void; readOnly?: boolean;
}) {
  return <div className="table-card"><table className="rt-table">
    <colgroup>{COLUMNS.map(col => <col key={col.key} style={col.width ? { width: col.width } : undefined} />)}</colgroup>
    <thead><tr>{COLUMNS.map(col => {
      if (col.key === 'summary' || col.key === 'done') return <th key={col.key}><span className="th-label">{col.label}</span></th>;
      const key = col.key, on = sort?.key === key;
      return <th key={key} aria-sort={on ? sort!.desc ? 'descending' : 'ascending' : 'none'}>
        <button className="th-sort" onClick={() => sortBy(key)}>{col.label}{on ? sort!.desc ? ' ↓' : ' ↑' : ''}</button>
      </th>;
    })}</tr></thead>
    <tbody>{jobs.map(j => {
      const id = String(j.id), [client, place] = clientLines(j), [posted, bids] = competitionLines(j);
      const connects = (j.details || {}).connects_cost;
      return <tr key={id} data-lead-id={id} className={`uw-row${id === drawerId ? ' sel' : ''}`} tabIndex={readOnly ? undefined : 0}
        onClick={readOnly ? undefined : e => { if (!(e.target as Element).closest('button, a')) toggle(id); }}
        onKeyDown={readOnly ? undefined : e => { if ((e.key === 'Enter' || e.key === ' ') && e.target === e.currentTarget) { e.preventDefault(); toggle(id); } }}>
        <td data-column="score"><span className={`uw-score ${scoreTone(j.score)}`}>{j.score == null ? '–' : j.score}</span></td>
        <td data-column="summary">
          {/* The link goes to the posting itself. Without it a member has to search Upwork
              by title to reread what the client actually wrote. */}
          {j.url
            ? <a className="rt-td-summary" href={j.url} target="_blank" rel="noopener" title={j.title}>{headlineText(j)}</a>
            : <span className="rt-td-summary" title={j.title}>{headlineText(j)}</span>}
          {jobFlags(j).map(flag => <span key={flag.text} className={`uw-flag ${flag.tone}`}>{flag.text}</span>)}
        </td>
        <td data-column="client"><span className={tone(clientTone(j))} title={(j.client || {}).rating ? undefined : 'No rating yet'}>{client}</span>
          <span className="uw-sub">{place}</span></td>
        <td data-column="competition"><span className={tone(postedTone(j))}>{posted}</span><span className={`uw-sub ${tone(bidsTone(j))}`}>{bids}</span></td>
        <td data-column="budget"><span className={tone(budgetTone(j))}>{budgetText(j)}</span>{connects != null ? <span className="uw-sub">{connects} connects · listed cost</span> : null}</td>
        <td data-column="step"><StepCell job={j} /></td>
        <td data-column="done"><LeadActions job={j} /></td>
      </tr>;
    })}</tbody>
  </table></div>;
}

// The posting itself, one click away. The list had it hidden behind the summary text
// and the board had it nowhere, so reading what a client actually wrote meant searching
// Upwork by title. The url survives prune, so this works on an old lead too.
function OnUpwork({ job }: { job: any }) {
  if (!job.url) return null;
  return <a className="on-upwork" href={job.url} target="_blank" rel="noopener"
    title="Open this job on Upwork" onClick={e => e.stopPropagation()}>
    <svg viewBox="0 0 16 16" fill="none" aria-hidden="true" className="on-upwork-icon">
      <path d="M6.5 3.5H3.2A.7.7 0 0 0 2.5 4.2v8.6a.7.7 0 0 0 .7.7h8.6a.7.7 0 0 0 .7-.7V9.5"
        stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M9.5 2.5h4v4M13.5 2.5 7 9" stroke="currentColor" strokeWidth="1.5"
        strokeLinecap="round" strokeLinejoin="round" />
    </svg>
    <span>Upwork</span>
  </a>;
}

function Board({ jobs, oldestFirst, drawerId, toggle }: { jobs: any[]; oldestFirst: boolean; drawerId: string | null; toggle: (id: string) => void }) {
  return <div className="board">{BOARD.map(stage => {
    const list = jobs.filter(j => j.status === stage)
      .sort((a, b) => ((daysInStage(b) ?? 0) - (daysInStage(a) ?? 0)) * (oldestFirst ? 1 : -1));
    return <section key={stage} className={`col stage-${stage}`}>
      <div className="col-head"><div className="col-title">{LABEL[stage]}</div><span className="col-count">{list.length}</span></div>
      <ul className="col-body">{list.length ? list.map(j => {
        const id = String(j.id), days = daysInStage(j), step = nextStep(j), state = waitingState(j);
        return <li key={id} className={`card${id === drawerId ? ' sel' : ''}`} tabIndex={0}
          onClick={e => { if (!(e.target as Element).closest('button')) toggle(id); }}
          onKeyDown={e => { if ((e.key === 'Enter' || e.key === ' ') && e.target === e.currentTarget) { e.preventDefault(); toggle(id); } }}>
          <span className="card-title" title={j.title}>{headlineText(j)}</span>
          <div className="card-meta">{[budgetText(j), days == null ? '' : `${days}d in stage`].filter(Boolean).join(' · ')}</div>
          {/* Say what is waiting on whom even when no command can do it: an offer to
              review is work, and a card without a chip used to look like nothing to do. */}
          {/* The state carries the wording when it has a date in it; otherwise the
              step's own label, because "Review offer" is work and "Waiting" is not. */}
          {/* A client who wrote last is the one thing a card says louder than its state, and
              the flag replaces the state line rather than repeating it as "Reply". */}
          {j.client_waiting ? <NewMessage job={j} />
            : <div className={`card-state state-${state.kind.replace(' ', '-')}${state.late ? ' tone-bad' : ''}`}>
              {state.kind === 'waiting' && step.label && step.label !== 'Waiting' ? step.label : state.detail}
            </div>}
          <div className="card-actions">
            {cardCommands(j, step).map((command: string) =>
              <CopyButton key={command} compact text={command} label={command.split(' ')[0]} />)}
            <OnUpwork job={j} />
          </div>
        </li>;
      }) : <li className="col-empty">Nothing here</li>}</ul>
    </section>;
  })}</div>;
}
