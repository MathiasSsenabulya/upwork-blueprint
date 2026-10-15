'use client';

import { useEffect, useRef, useState } from 'react';
import { useCockpit } from '@/lib/context';
import { FILTER_FIELDS, filterCommand, optionsFor } from '@/lib/filter.mjs';
import CopyButton from './CopyButton';

/** The job filter, picked here and saved by /find-jobs (12.10.2026).
 *
 * The cockpit never writes the filter, so this builds the one line to paste into Claude Code,
 * where the filter is checked, stored and searched with. Until that run the list still
 * shows what the old filter let through, and the note under the choices says so.
 */
export default function FilterMenu() {
  const { state } = useCockpit();
  const saved: Record<string, string> | null = state?.filter || null;
  const [open, setOpen] = useState(false);
  const [picked, setPicked] = useState<Record<string, string>>({});
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onPointer = (event: PointerEvent) => { if (!boxRef.current?.contains(event.target as Node)) setOpen(false); };
    const onKey = (event: KeyboardEvent) => { if (event.key === 'Escape') setOpen(false); };
    document.addEventListener('pointerdown', onPointer);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('pointerdown', onPointer);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  // An older code/cockpit.py sends no filter: no menu is better than one that guesses.
  if (!saved) return null;
  const values = { ...saved, ...picked };
  const changed = FILTER_FIELDS.some(field => values[field.key] !== saved[field.key]);
  const command = filterCommand(values);

  return <div className="filter-menu" ref={boxRef}>
    <button type="button" className="due-toggle with-icon" aria-expanded={open} aria-controls="job-filter"
      onClick={() => setOpen(value => !value)}>
      <svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2.5 4h11M4.5 8h7M6.5 12h3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" /></svg>
      Job filter</button>
    {open ? <div className="filter-pop" id="job-filter" role="dialog" aria-label="Job filter">
      <div className="filter-rows">{FILTER_FIELDS.map(field => <label key={field.key} className="filter-row">
        <span>{field.label}</span>
        <select value={values[field.key]} onChange={event => setPicked(current => ({ ...current, [field.key]: event.target.value }))}>
          {optionsFor(field, values[field.key]).map(([value, label]: string[]) => <option key={value} value={value}>{label}</option>)}
        </select>
      </label>)}</div>
      <code className="filter-command">{command}</code>
      <div className="filter-foot">
        <span className="filter-note">{changed ? 'Not saved yet. Paste it into Claude Code.' : 'This is your saved filter.'}</span>
        <CopyButton text={command} label="Copy" />
      </div>
    </div> : null}
  </div>;
}
