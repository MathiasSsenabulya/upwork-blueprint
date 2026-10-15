import { moveLead } from '@/lib/server/move.mjs';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
type Context = { params: Promise<{ id: string }> };

/** The X: a Not applied lead leaves the list. */
export function POST(req: Request, { params }: Context) {
  return moveLead(req, params, 'new', ['set', 'skipped'], 'Only a job you have not applied to can be removed here.');
}

/** Undo: it comes back as Not applied. */
export function DELETE(req: Request, { params }: Context) {
  return moveLead(req, params, 'skipped', ['undo'], 'That job is not on the removed list any more.');
}
