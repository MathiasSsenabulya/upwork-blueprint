'use client';

import { useState } from 'react';
import { useCockpit } from '@/lib/context';

/** The flag on a lead whose client wrote last, and the one click that clears it (13.10.2026).
 *
 * "Mark as read" is for the message that needs no answer, a "sounds good": without it the
 * lead sits on the member's side until they write back. It goes through code/pipeline.py,
 * touches no Upwork tool, and the toast undoes it. The flag returns when the client writes again.
 */
export default function NewMessage({ job }: { job: any }) {
  const { api, load, toast } = useCockpit();
  const [busy, setBusy] = useState(false);
  if (!job.client_waiting) return null;

  const path = `/api/job/${job.id}/read`;
  const markRead = async () => {
    setBusy(true);
    const result = await api(path, 'POST');
    setBusy(false);
    if (!result.ok) { toast(result.data?.error || 'That did not work. Run /dashboard and try again.'); return; }
    await load();
    toast('Marked as read.', { label: 'Undo', run: async () => {
      const back = await api(path, 'DELETE');
      await load();
      toast(back.ok ? 'New message again.' : back.data?.error || 'Could not undo that.');
    } });
  };

  return <div className="new-message">
    <span className="new-message-flag">New message</span>
    <button type="button" className="mark-read" disabled={busy} onClick={() => void markRead()}
      title="No reply needed: take it off your side until they write again">Mark as read</button>
  </div>;
}
