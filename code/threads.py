#!/usr/bin/env python3
"""Client threads: turns what Upwork's message list returns into the cockpit's chat.

    python3 code/threads.py save <job_id> --file <list_messages.json>|- [--merge]
    python3 code/threads.py find "<client name or lead id>"
    python3 code/threads.py adopt <room_id> --client "<name>" --title "<room name>"
                                  [--status replied|won] [--last-at <time of the newest message>]

Upwork hands messages back newest first, each wrapped in a marker for untrusted
text, with HTML entities, escaped markdown and system events ("System event:
ended", "Kyle ended the contract") mixed in with real messages. This script is
the one place that cleans them: oldest first, plain text, your messages marked as
yours, events as events. The result is jobs/<id>/thread.json, which the cockpit's
panel reads. It is Upwork content, so `pipeline.py prune` deletes it after
KEEP_CHAT_HOURS (90 days).

`find` is where /message starts: it answers which lead a client's name belongs to
from what is saved here, so no Upwork call is spent on a room already known.
`adopt` gives a room that belongs to no lead its own record, written by pipeline.py.
`save --merge` adds a page to the saved conversation, so /message can read a thread
back to its first message a page at a time and a read-back never replaces the history.
"""
import argparse
import datetime
import hashlib
import html
import json
import pathlib
import re
import subprocess
import sys
import os
import tempfile
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
import pipeline  # noqa: E402  (read-only use: load, jobs_dir)

WRAPPER = re.compile(r'</?untrusted_participant_content>')
SYSTEM_EVENT = re.compile(r'^System event: (\w+)\.')
# Only the event whose meaning the room card confirms gets a plain name; the rest
# stay as Upwork says them rather than as a guess.
EVENT_WORDS = {'ended': 'Contract ended'}
NOTICE = re.compile(r'(\*\*[^*]+\*\* (ended the contract|wants to schedule[^\n]*))|accepted your offer', re.I)


def write_json(target, record):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=target.parent, prefix='.thread-', delete=False) as handle:
        temp = pathlib.Path(handle.name)
        json.dump(record, handle, indent=2, ensure_ascii=False)
    try:
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)


def clean(text):
    text = html.unescape(WRAPPER.sub('', text or '')).strip()
    return re.sub(r'\\([.\-*_#()\[\]])', r'\1', text)


def normalize(items):
    """Raw list_messages edges or already clean messages in, clean messages out, oldest first."""
    out, seen = [], set()
    for item in items or []:
        node = item.get('node', item) if isinstance(item, dict) else {}
        if 'createdDateTime' in node or 'from_side' in node:
            text = clean(node.get('message'))
            event = SYSTEM_EVENT.match(text)
            kind = 'event' if event or NOTICE.search(text) else 'message'
            if event:
                text = EVENT_WORDS.get(event.group(1), f'Upwork: {event.group(1)}')
            elif kind == 'event':
                text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text).replace('Please check your offers for details.', '').strip()
            side = 'me' if node.get('from_self') or node.get('from_side') == 'freelancer' else 'client'
            message = {'id': node.get('id'), 'from': 'system' if kind == 'event' else side,
                       'name': clean(node.get('from')), 'at': node.get('createdDateTime'), 'text': text, 'kind': kind}
        else:
            message = {**node, 'kind': node.get('kind', 'message')}
        key = message.get('id') or (message.get('at'), message.get('text'))
        if key in seen:
            continue
        seen.add(key)
        out.append(message)
    out.sort(key=lambda m: str(m.get('at') or ''))
    return out


def edges_of(raw):
    """Accepts the whole list_messages response, its edges, or a plain list."""
    if isinstance(raw, list):
        return raw
    data = raw.get('data', raw)
    return ((data.get('roomStories') or {}).get('edges')) or data.get('messages') or []


def save(job_id, raw, room_id=None, awaiting=None, merge=False):
    """Replaces the saved thread, or with merge adds to it and keeps what it already says
    about the room and the turn unless this call says otherwise."""
    folder = pipeline.jobs_dir() / job_id
    folder.mkdir(parents=True, exist_ok=True)
    before = read_thread(job_id) if merge else {}
    messages = normalize(list(before.get('messages') or []) + list(edges_of(raw)))
    record = {'fetched_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
              'room_id': room_id or before.get('room_id'),
              'awaiting_reply_from': awaiting or before.get('awaiting_reply_from'), 'messages': messages}
    write_json(folder / 'thread.json', record)
    return messages


def cmd_save(args):
    if not any(j.get('id') == args.job_id for j in pipeline.load()):
        print(f'ABORT: job "{args.job_id}" is not in the pipeline.', file=sys.stderr)
        return 1
    raw = json.loads(sys.stdin.read() if args.file == '-' else pathlib.Path(args.file).read_text(encoding='utf-8'))
    messages = save(args.job_id, raw, args.room, args.awaiting, args.merge)
    events = sum(1 for m in messages if m['kind'] == 'event')
    print(f'{args.job_id}: {len(messages) - events} messages and {events} events saved.')
    return 0


def words(text):
    """A name as the words someone would type for it: lower case, no accents, no punctuation."""
    plain = ''.join(c for c in unicodedata.normalize('NFKD', str(text or '')) if not unicodedata.combining(c))
    return re.sub(r'[^\w\s]', ' ', plain.casefold()).split()


def read_thread(job_id):
    """A lead's saved thread, or an empty one when nothing was saved or it does not parse."""
    try:
        thread = json.loads((pipeline.jobs_dir() / job_id / 'thread.json').read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return thread if isinstance(thread, dict) else {}


def find(query, jobs, thread_for):
    """Every lead whose client goes by this name. A name is the contract's client or a
    person who wrote in the thread as the client: never the member, an event or the job
    title, which share words with half the pipeline. Every word typed must start a word of
    one name: "ann" finds Ann and Annette, never Joanna. A lead id, which is what the
    dashboard copies, finds that one lead whatever its client is called."""
    wanted = words(query)
    matches = []
    for job in jobs if wanted else []:
        thread = thread_for(job['id'])
        messages = [m for m in thread.get('messages') or [] if isinstance(m, dict)]
        names = list(dict.fromkeys(
            name for name in [job.get('contract_client')] + [m.get('name') for m in messages if m.get('from') == 'client']
            if name))
        if str(query).strip() != job['id'] and not any(
                all(any(part.startswith(word) for part in words(name)) for word in wanted) for name in names):
            continue
        spoken = [m for m in messages if m.get('kind') != 'event']
        matches.append({'id': job['id'], 'names': names, 'status': job.get('status'), 'title': job.get('title') or '',
                        'room_id': job.get('room_id') or thread.get('room_id'), 'messages': len(spoken),
                        'last_at': max((str(m.get('at') or '') for m in spoken), default='')})
    return matches


def cmd_find(args):
    matches = find(args.name, pipeline.load(), read_thread)
    if not matches:
        print('NONE: no lead in the pipeline goes by that name.')
        return 0
    for match in matches:
        room = f"room {match['room_id']}" if match['room_id'] else 'no room saved'
        saved = f"{match['messages']} messages saved, last {match['last_at'][:10]}" if match['messages'] else 'no thread saved'
        names = ', '.join(match['names']) or 'no name saved'
        print(f"{match['id']} · {names} · {match['status']} · {room} · {saved} · {match['title']}")
    return 0


def run_pipeline(*arguments, value):
    """One write through the sole writer of the pipeline. Its own words come back on a failure."""
    out = subprocess.run([sys.executable, str(ROOT / 'code' / 'pipeline.py'), *arguments, '--file', '-'],
                         input=json.dumps(value), capture_output=True, text=True)
    if out.returncode:
        print(out.stderr.strip(), file=sys.stderr)
    return out.returncode == 0


def room_of(job):
    """The room a lead talks in: on its record, or only in its saved thread after a plain save."""
    return job.get('room_id') or read_thread(job['id']).get('room_id')


def cmd_adopt(args):
    """A client who never came through /find-jobs still gets a thread, checked drafts and a
    log of what was sent, and all three hang off a lead record. A room a lead already owns
    is left alone. A room named exactly like one lead that has no room joins that lead: it
    is the reply to a proposal nobody synced yet. Only then is a record made, with an id
    built the way sync.py builds one for an unmatched contract and the room's own name as
    its title, so a later sync that finds an offer or contract with that title lands on it."""
    jobs = pipeline.load()
    owner = next((j for j in jobs if room_of(j) == args.room), None)
    if owner:
        print(f"{owner['id']}: that room already belongs to this lead.")
        return 0
    last_at = pipeline.parse_verified_timestamp(args.last_at) if args.last_at else None
    if args.last_at and not last_at:
        print('ABORT: --last-at needs the ISO time of the newest message, with a timezone and not in the future.',
              file=sys.stderr)
        return 1
    title = ' '.join(args.title.split())
    same_title = [j for j in jobs if ' '.join(str(j.get('title') or '').split()).casefold() == title.casefold()
                  and not room_of(j)]
    job_id = str(int.from_bytes(hashlib.sha256(f'room:{args.room}'.encode()).digest()[:10], 'big'))
    waiting = next((j for j in jobs if j['id'] == job_id), None)
    lead = same_title[0] if len(same_title) == 1 else waiting
    if not lead:
        record = {'id': job_id, 'title': title, 'url': '', 'status': args.status, 'found_via': ['message'],
                  'notes': 'room opened by /message', 'imported': True, 'application_date_unknown': True,
                  **({'last_activity_at': last_at} if last_at else {})}
        if not run_pipeline('add', value=record):
            return 1
    target = lead['id'] if lead else job_id
    named = {} if lead and lead.get('contract_client') else {'contract_client': args.client}
    if not run_pipeline('record', target, value={'room_id': args.room, **named}):
        return 1
    print(f"{target}: that room now belongs to this lead." if lead
          else f'{target}: {args.client} is in the pipeline as {args.status}.')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('save', help='Save one client thread for the cockpit.')
    p.add_argument('job_id')
    p.add_argument('--file', required=True, help='The list_messages response as JSON. "-" reads stdin.')
    p.add_argument('--room', help='The saved Upwork room id.')
    p.add_argument('--awaiting', choices=('you', 'them'), help="The room card's awaiting_reply_from.")
    p.add_argument('--merge', action='store_true', help='Add these messages to the saved thread instead of replacing it.')
    p.set_defaults(func=cmd_save)
    p = sub.add_parser('find', help='Which lead a client name belongs to, from what is saved.')
    p.add_argument('name', help='A client name, or a lead id as the dashboard copies it.')
    p.set_defaults(func=cmd_find)
    p = sub.add_parser('adopt', help='Give a room that belongs to no lead its own record.')
    p.add_argument('room')
    p.add_argument('--client', required=True, help='The client as the room names them.')
    p.add_argument('--title', required=True, help="The room's own name, so a later sync can match it.")
    p.add_argument('--status', choices=('replied', 'won'), default='replied',
                   help='won when a contract with this client exists, otherwise replied.')
    p.add_argument('--last-at', help='ISO time of the newest message, so an old thread does not look fresh.')
    p.set_defaults(func=cmd_adopt)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
