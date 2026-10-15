import { markRead } from '@/lib/server/move.mjs';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
type Context = { params: Promise<{ id: string }> };

/** Mark as read: the client's last message needs no answer, so the lead stops waiting on the member. */
export function POST(req: Request, { params }: Context) {
  return markRead(req, params, false);
}

/** Undo: the lead is back on the member's side. */
export function DELETE(req: Request, { params }: Context) {
  return markRead(req, params, true);
}
