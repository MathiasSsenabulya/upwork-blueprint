'use client';
// The contract every cockpit component builds on. components/Cockpit.tsx provides
// it; nothing else talks to the server directly. The cockpit reads, and its two writes are
// the check and the X on a Not applied lead (lib/server/move.mjs).
import { createContext, useContext } from 'react';

export type Job = any;
export type State = any;
/** One thing a toast can offer, such as undoing what was just done. */
export type ToastAction = { label: string; run: () => void };

export type CockpitApi = {
  token: string;
  state: State | null;                  // /api/state: jobs, sync, tracker, saved analytics, daily voyage
  load: () => Promise<void>;
  api: (path: string, method?: 'GET' | 'POST' | 'DELETE') => Promise<{ ok: boolean; data: any }>;
  toast: (message: string, action?: ToastAction) => void;
  drawerId: string | null;
  openDrawer: (id: string) => void;
  closeDrawer: () => void;
  openAnalyticsLeads: (ids: (string | number)[]) => void;
};

export const CockpitContext = createContext<CockpitApi | null>(null);

export function useCockpit(): CockpitApi {
  const ctx = useContext(CockpitContext);
  if (!ctx) throw new Error('useCockpit needs <CockpitProvider>');
  return ctx;
}
