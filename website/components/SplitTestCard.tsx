'use client';

type Side = { leads: number; wins: number; done: number };
type Test = {
  stage: string; started_at: string; a: string; b: string; win_words: string; mover?: string | null;
  sides: { A: Side; B: Side }; chance_b: number; call: 'ship B' | 'keep A' | 'keep going';
};

const UNIT: Record<string, string> = { proposal: 'proposal', messages: 'conversation', call: 'call', 'after-call': 'call', close: 'offer' };
const NEED = 5;          // finished leads a side before a call, as split_test.py decides
const SHIP = 80;         // B ships at this chance of beating A
const STATUS: Record<Test['call'], [string, string]> = {
  'ship B': ['New way wins', 'win'],
  'keep A': ['Old way stays', 'stay'],
  'keep going': ['', 'run'],
};
const CALLS: Record<Test['call'], string> = {
  'ship B': 'The new way wins. Run /analytics to make it your default.',
  'keep A': 'The new way is not better. Run /analytics to keep the old one and try the next idea.',
  'keep going': 'No clear winner yet.',
};

/** "New proposal: 1. social proof, 2. the result" splits into its name and its parts. */
function split(text: string) {
  const pieces = text.split(/\s*\d\.\s+/);
  const parts = pieces.slice(1).map(p => p.replace(/[,.;]\s*$/, '').trim()).filter(Boolean)
    .map(p => p.charAt(0).toUpperCase() + p.slice(1));
  return parts.length >= 2 ? { name: pieces[0].replace(/:\s*$/, '').trim(), parts } : { name: '', parts: [text] };
}

function day(iso: string) {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso.slice(0, 10) : d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

/** The one split test: the old way against the new one, side by side, and how close a call is.
 *  Code computes every number; this only shows it (split_test.py status says the same). */
export default function SplitTestCard({ test }: { test: Test | null | undefined }) {
  if (!test) return null;
  const unit = UNIT[test.stage] || 'lead';
  const started = test.sides.A.done + test.sides.B.done > 0;
  const chance = Math.round(100 * test.chance_b);
  const a = split(test.a), b = split(test.b);
  const title = a.name && b.name ? `${a.name} vs ${b.name.charAt(0).toLowerCase()}${b.name.slice(1)}` : 'The old way vs the new way';
  const [status, tone] = started ? STATUS[test.call] : ['Waiting for results', 'wait'];
  const how = test.stage === 'profile'
    ? 'Your profile changes once: the 28 days before are A, everything after is B.'
    : `Each new ${unit} gets A or B.`;
  const side = (letter: 'A' | 'B', what: { name: string; parts: string[] }) => {
    const s = test.sides[letter];
    return <article className={`st-side st-${letter.toLowerCase()}`}>
      <header>
        <span className="st-letter">{letter}</span>
        <span className="st-name">{what.name || (letter === 'A' ? 'The old way' : 'The new way')}</span>
      </header>
      <ol className="st-parts">{what.parts.map((part, i) => <li key={i}>{part}</li>)}</ol>
      <footer className="st-count">
        <span className="st-dots" aria-hidden="true">{Array.from({ length: NEED }, (_, i) =>
          <i key={i} className={i < s.done ? 'on' : undefined}/>)}</span>
        <span>{s.done ? `${s.wins} of ${s.done} ${test.win_words}` : `0 of ${NEED} finished`}</span>
      </footer>
    </article>;
  };
  return <section className="st" aria-label="Split test">
    <header className="st-head">
      <div>
        <p className="cl-grp">The test</p>
        <h2 className="st-title">{title}</h2>
      </div>
      <span className={`st-status st-${tone}`}>{status || `B ${chance}% likely to win`}</span>
    </header>
    <p className="st-sub">{how} The new way becomes your default once it is {SHIP}% likely to win, after {NEED} finished {unit}s a side. Started {day(test.started_at)}.</p>
    <div className="st-sides">{side('A', a)}{side('B', b)}</div>
    {started && <div className="st-foot">
      <div className="st-meter">
        <progress max={100} value={chance} aria-label={`B is ${chance}% likely to beat A`}/>
        <span className="st-line" aria-hidden="true"/>
      </div>
      <p><strong>B is {chance}% likely to beat A.</strong> {CALLS[test.call]}</p>
    </div>}
  </section>;
}
