'use client';

import { useState } from 'react';
import { useCockpit } from '@/lib/context';

/** The check and the X on a Not applied lead (12.10.2026), the two things the dashboard writes.
 *
 * Check: I sent this one, the same move as `/proposal <id> submitted`. X: not for me, off the
 * list. Both go through code/pipeline.py, neither touches Upwork, and the toast undoes either.
 * The X carries no reason, so the next search learns nothing from it: a skip with a reason
 * still goes through `/find-jobs skip <id> <reason>`. Leads further along move through /dashboard.
 */
export default function LeadActions({ job, labels = false }: { job: any; labels?: boolean }) {
  const { api, load, toast, drawerId, closeDrawer } = useCockpit();
  const [busy, setBusy] = useState(false);
  if (job.status !== 'new') return null;

  const move = async (kind: 'sent' | 'skip') => {
    const path = `/api/job/${job.id}/${kind}`;
    setBusy(true);
    const result = await api(path, 'POST');
    setBusy(false);
    if (!result.ok) { toast(result.data?.error || 'That did not work. Run /dashboard and try again.'); return; }
    if (kind === 'skip' && drawerId === String(job.id)) closeDrawer();
    await load();
    toast(kind === 'sent' ? 'Marked as sent.' : 'Removed from your list.', { label: 'Undo', run: async () => {
      const back = await api(path, 'DELETE');
      await load();
      toast(back.ok ? 'Back on your unsent list.' : back.data?.error || 'Could not undo that.');
    } });
  };

  return <span className={`lead-actions${labels ? ' labelled' : ''}`}>
    <button type="button" className="row-act sent" disabled={busy} onClick={() => void move('sent')}
      aria-label="I sent this one" title="I sent this one">
      <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <path d="M3.5 8.5l3 3 6-7" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
      </svg>{labels ? <span>Sent</span> : null}
    </button>
    <button type="button" className="row-act remove" disabled={busy} onClick={() => void move('skip')}
      aria-label="Not for me, remove it" title="Not for me, remove it">
      <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      </svg>{labels ? <span>Remove</span> : null}
    </button>
  </span>;
}
