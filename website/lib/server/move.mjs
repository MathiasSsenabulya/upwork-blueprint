// The three things the cockpit writes. The check on a row says "I sent this one" and the X
// takes a lead off the list (12.10.2026). "Mark as read" on a card says the client's last
// message needs no answer (13.10.2026). The toast after each undoes it. All three go through
// code/pipeline.py, which stays the only writer of the pipeline, and none touches Upwork.
// The stage is checked here and not only in the page, so nothing further along can be
// moved by a stray request.
import { BOARD } from '../stages.mjs';
import { guard, json } from './guard.mjs';
import { ID, pyJson, runPython } from './root.mjs';

export async function moveLead(req, params, from, args, refusal) {
  const refused = guard(req);
  if (refused) return refused;
  const { id } = await params;
  if (!ID.test(id)) return json({ error: 'bad job' }, 400);
  const job = await pyJson('cockpit.py', ['job', id]);
  if (!job) return json({ error: 'not found' }, 404);
  if (job.status !== from) return json({ error: refusal }, 409);
  const done = await runPython('pipeline.py', [args[0], id, ...args.slice(1)]);
  return done.ok ? json({ ok: true }) : json({ error: 'The pipeline refused the change. Run /dashboard and try again.' }, 500);
}

/** Mark as read, and its undo. Only a lead with a conversation, and only while its client is the one waiting. */
export async function markRead(req, params, undo) {
  const refused = guard(req);
  if (refused) return refused;
  const { id } = await params;
  if (!ID.test(id)) return json({ error: 'bad job' }, 400);
  const job = await pyJson('cockpit.py', ['job', id]);
  if (!job) return json({ error: 'not found' }, 404);
  if (!BOARD.includes(job.status)) return json({ error: 'Only a lead with a conversation can be marked as read.' }, 409);
  if (!undo && !job.client_waiting) return json({ error: 'No new message is waiting on this lead.' }, 409);
  const done = await runPython('pipeline.py', ['read', id, ...(undo ? ['--undo'] : [])]);
  return done.ok ? json({ ok: true }) : json({ error: 'The pipeline refused the change. Run /dashboard and try again.' }, 500);
}
