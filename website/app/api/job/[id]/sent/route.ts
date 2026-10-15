import { moveLead } from '@/lib/server/move.mjs';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
type Context = { params: Promise<{ id: string }> };

/** The check: the member sent this application on Upwork. The same move as `/proposal <id> submitted`. */
export function POST(req: Request, { params }: Context) {
  return moveLead(req, params, 'new', ['set', 'applied'], 'Only a job you have not applied to can be marked as sent.');
}

/** Undo: it goes back to Not applied, and the day's count with it. */
export function DELETE(req: Request, { params }: Context) {
  return moveLead(req, params, 'applied', ['undo'], 'That job has moved on since, so it stays where it is.');
}
