'use client';

type Stage = { key: string; label: string; in: number; out: number; out_label: string; tone?: string };
type Funnel = { label: string; stages?: Stage[]; leak_stage?: number | null };

const TONE_WORD: Record<string, string> = { good: 'On track', close: 'Too early to tell', bad: 'Behind', none: 'No data yet' };
const IN_WORD: Record<string, string> = { proposals: 'sent', messaging: 'replies', calls: 'calls', offers: 'offers' };
// Which checks each stage opens. Closing a deal is accepting an offer, so it has no stage of its own.
export const STAGE_AREA = ['replies', 'conversations', 'calls', 'closing'];

/** Four stages left to right, one per step a member works on: proposals, messaging, calls, offers.
 *  Each shows what went in and what came out, carries stripes in its state's colour, and opens its checks. */
export default function HorizontalFunnel({ funnel, selected, onSelect }:
  { funnel: Funnel | null | undefined; selected?: string; onSelect?: (area: string) => void }) {
  const stages = funnel?.stages;
  if (!stages?.length) return null;
  const leak = funnel?.leak_stage;
  return <section className="hf" aria-label="Your funnel">
    <p className="hf-label">{funnel?.label}. Click a stage to see its checks.</p>
    <ol className="hf-steps">
      {stages.map((stage, i) => {
        const share = stage.in ? Math.round(100 * stage.out / stage.in) : null;
        const tone = stage.tone || 'none';
        const area = STAGE_AREA[i];
        return <li key={stage.key} className={`hf-step hf-${tone}${leak === i ? ' hf-stuck' : ''}${selected === area ? ' hf-open' : ''}`}>
          {i > 0 && <span className="hf-arrow" aria-hidden="true">→</span>}
          <button type="button" className="hf-box" title={TONE_WORD[tone]} aria-label={`${stage.label}: ${stage.out} of ${stage.in}, ${TONE_WORD[tone].toLowerCase()}`} aria-pressed={selected === area} onClick={() => onSelect?.(area)}>
            <span className="hf-name">{stage.label}</span>
            <strong>{stage.out}<small> of {stage.in}</small></strong>
            <span>{IN_WORD[stage.key] || 'in'} {stage.out_label}{share !== null ? ` · ${share}%` : ''}</span>
            <em>{TONE_WORD[tone]}</em>
          </button>
          {leak === i && <span className="hf-flag">Stuck here</span>}
        </li>;
      })}
    </ol>
  </section>;
}
