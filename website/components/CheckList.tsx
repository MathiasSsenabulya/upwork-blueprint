'use client';

type Item = { key: string; name: string; status: string; note: string; standard: string; source: string; how: string };
type Section = { key: string; name: string; rating: string; items: Item[] };
type Call = { job_id: string; title: string; date: string; better: string; checks: Record<string, { status: string }> };
type Mover = { title: string; why: string; do: string; test?: { stage: string }; evidence?: { name: string }[] };
type Area = { title: string; coach?: string[]; movers?: Mover[]; sections: Section[]; calls?: Call[] };
type Diagnosis = { week: string; stuck: string; areas: Record<string, Area> };

const NOT_CHECKED = 'Not checked this week.';
const RATING: Record<string, string> = { holding_back: 'Holding you back', weak: 'Could be better', fine: 'Fine', unknown: 'No data yet' };
const TONE: Record<string, string> = { holding_back: 'now', weak: 'hold', fine: 'fine', unknown: 'rest' };
const MARK: Record<string, string> = { ok: '✓', missing: '✗', weak: '~', optional: '○', unknown: '?' };
const MARK_WORD: Record<string, string> = { ok: 'In place', missing: 'Missing', weak: 'Weak', optional: 'Optional', unknown: 'Not known' };

/** One stage's checks in the CRO audit's layout: the 1 to 3 changes that get 90% of this stage's result
 *  (the one being split tested is tagged), any coach's note, then one card per section with only what was
 *  actually checked. Calls also list each call with how it could have gone better. */
export default function CheckList({ diagnosis, week, area }: { diagnosis: Diagnosis | null | undefined; week?: string; area?: string }) {
  if (!diagnosis?.areas || (week && diagnosis.week !== week)) return null;
  const key = area && diagnosis.areas[area] ? area : diagnosis.stuck;
  const step = diagnosis.areas[key];
  if (!step?.sections?.length) return null;
  const sections = step.sections
    .map(s => ({ ...s, items: s.items.filter(i => i.note !== NOT_CHECKED) }))
    .filter(s => s.items.length);
  const items = sections.flatMap(s => s.items);
  const chips: [string, number, string][] = [['Missing', items.filter(i => i.status === 'missing').length, 'now'],
    ['Weak', items.filter(i => i.status === 'weak').length, 'hold'], ['In place', items.filter(i => i.status === 'ok').length, 'fine']];
  return <section className="cl" aria-label={`Checks: ${step.title}`}>
    <div className="cl-sum">
      <p className="cl-big"><span className="cl-n">{step.title}</span>{key === diagnosis.stuck && <span className="cl-k">where you're stuck</span>}</p>
      <div className="cl-chips">{chips.filter(([, n]) => n).map(([label, n, tone]) =>
        <span key={label} className={`cl-chip cl-${tone}`}>{label} {n}</span>)}</div>
      {!!step.movers?.length && <>
        <p className="cl-grp">What gets you 90% of the result at this stage</p>
        <ol className="mv-list cl-movers">{step.movers.map((m, i) => <li key={i}>
          <strong>{m.title}{m.test && <span className="mv-test">Split testing this</span>}</strong>
          <p className="mv-why">{m.why}</p>
          <p className="mv-do"><span>Do this:</span> {m.do}</p>
          {!!m.evidence?.length && <p className="mv-from">From your data: {m.evidence.map(e => e.name).join(' · ')}</p>}
        </li>)}</ol>
      </>}
      {!!step.coach?.length && <>
        <p className="cl-grp">Coach's note</p>
        <ul className="cl-coach">{step.coach.map((line, i) => <li key={i}>{line}</li>)}</ul>
      </>}
    </div>
    {sections.map((s, i) => <article key={s.key} className={`cl-card cl-${TONE[s.rating] || 'rest'}`}>
      <header>
        <span className="cl-num">{i + 1}</span>
        <span className="cl-is">{s.name}</span>
        <span className="cl-vd">{RATING[s.rating] || s.rating}</span>
      </header>
      {s.items.every(it => it.status === 'unknown' && it.note === s.items[0].note) && s.items.length > 1
        ? <p className="cl-gap">{s.items[0].note} <span>Each call is checked for: {s.items.map(it => it.name.toLowerCase()).join(', ')}.</span></p>
        : <ul className="cl-items">{s.items.map(it => <li key={it.key} className={`cl-it cl-it-${it.status}`}>
        <span className="cl-mark" aria-label={MARK_WORD[it.status]} title={MARK_WORD[it.status]}>{MARK[it.status] || '?'}</span>
        <span className="cl-it-body">
          <span className="cl-it-name">{it.name}</span> <span className="cl-it-note">{it.note}</span>
          {(it.status === 'missing' || it.status === 'weak') && <small className="cl-it-good">Good: {it.standard} · {it.source}</small>}
        </span>
      </li>)}</ul>}
    </article>)}
    {!!step.calls?.length && <>
      <p className="cl-grp cl-grp-list">Call by call</p>
      {step.calls.map(call => {
        const missed = Object.values(call.checks).filter(c => c.status !== 'ok').length;
        return <article key={call.job_id} className="cl-card cl-call">
          <header>
            <span className="cl-num">{call.date.slice(5)}</span>
            <span className="cl-is">{call.title}</span>
            <span className="cl-vd">{missed ? `${missed} to work on` : 'Strong call'}</span>
          </header>
          <p className="cl-why"><strong>Better:</strong> {call.better}</p>
        </article>;
      })}
    </>}
  </section>;
}
