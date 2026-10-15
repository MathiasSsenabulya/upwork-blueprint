'use client';

import type { MouseEvent } from 'react';
import { useCockpit } from '@/lib/context';

/** The older way to copy, for a page the clipboard API refuses, such as one opened inside an editor's preview. */
function copyWithoutClipboardApi(text: string) {
  const area = document.createElement('textarea');
  area.value = text;
  area.readOnly = true;
  area.className = 'copy-scratch';
  document.body.appendChild(area);
  area.select();
  try {
    return document.execCommand('copy');
  } catch {
    return false;
  } finally {
    area.remove();
  }
}

/** Copies a command for Claude Code, or a text for Upwork. The cockpit never runs it.
 *
 * A command button says the command and nothing else (13.10.2026): its label and its tooltip
 * are what lands in the clipboard, so no "Copy" can ride along when a member copies by hand. */
export default function CopyButton({ text, label, compact = false }: { text: string; label: string; compact?: boolean }) {
  const { toast } = useCockpit();
  const copied = () => toast(text.startsWith('/') ? 'Copied. Paste it into Claude Code.' : 'Copied.');
  const secondTry = () => {
    if (copyWithoutClipboardApi(text)) copied();
    else toast('Copy was blocked. Select the text and copy it by hand.');
  };
  const copy = (event: MouseEvent) => {
    event.stopPropagation();
    if (!navigator.clipboard?.writeText) { secondTry(); return; }
    navigator.clipboard.writeText(text).then(copied, secondTry);
  };
  return <button className={`copy-button${compact ? ' compact' : ''}`} onClick={copy}
    title={text.startsWith('/') ? text : `Copy ${text}`}>{label}</button>;
}
