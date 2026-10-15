# Follow-up rules

What: a context-based sequence for leads in touch and for previous clients.
Basis: reasoned; the only data point is one imported conversation (12 September 2026).
Next: run `/dashboard` without a job id each morning; it runs this sequence first.

The point is to make the next decision easy, not to maximize message count.
Context can stop a sequence or move its date.

## Where every thread is heading

**A call.** That is the call to action of the whole conversation: a client who has spoken
to the member hires far more easily than one who has only read them. It does not mean
every message asks for one. It means each message moves one step closer: answer the
question, show one thing worth talking about, and offer the call when there is something
to talk through. Once a call is booked, `/dashboard` writes the member's brief for it (`/sales-call-prep`).
**After the call, the next message is the proposal**
(`/sales-call-proposal`), sent while the call is fresh, and the follow-ups below then
chase that proposal like any other open decision.

## Reply now

When `awaiting_reply_from` is `you`, answer today. This is a reply, not a dormant
lead follow-up, and it does not consume a sequence step. A client question,
requested change, call request or offer always outranks scheduled follow-ups.

**Marked as read is not waiting.** A "sounds good" needs no answer, and the member clears
it with Mark as read on the dashboard (`python3 code/pipeline.py read <id>`). Until the
client writes again that lead is not waiting on the member: draft no reply for it and set
no date because of it. `client_waiting` in `python3 code/cockpit.py state` already says so.

## In touch

Use `active` for every lead that has answered (`replied`, `call` or `offer`), anywhere
on the way from the first reply to the closed deal: before a call, after it, and after
the proposal has gone out. **Follow up on day 3 and on day 7 of silence**, counted in
business days from the last message, then leave the lead alone until the client returns.

**The days are soft.** They are the default, not a rule Upwork set: a member who wants
another rhythm, such as a message a day for a week to test it, writes the days into
`**Follow-up days:**` in `context/me.md` ("1, 2, 3, 4, 5"), and
`python3 code/pipeline.py follow-up` plans every new sequence from that line. Say which
rhythm a lead is on when you report it.

Each message gives one new reason to answer (below). A generic status request does not
count as value.

## Previous client

Use `reactivation` only for a `won` client with a positive relationship and a
real reason to reconnect. An unfinished promise or stated date overrides this
lane and becomes a normal task.

Allow two messages, 30 then 60 business days apart. Lead with a relevant idea,
change or next project based on the completed work. Do not send a vague
"hope you're well" sequence.

## Applied, lost, skipped and new

An `applied` proposal has no room until the client writes, so it has no follow-up
and creates no task. After 14 full days without a client reply `/dashboard` lists it as
stale and asks whether to set `lost`; Lost is always the member's call.

Do not follow up with `new` or `skipped` jobs. A `lost` lead gets one future
check only when the client explicitly named timing or budget as the reason and a
date makes sense. Otherwise it stays closed.

## Context beats the cadence

Stop immediately after an explicit no, a request for no more contact, evidence
that another freelancer was hired, or a move to another agreed communication
channel. Do not duplicate the conversation across channels.

Honor a date the client named. Follow up on the next business day after a missed
promise, not on the generic cadence.

Count meaningful client turns, not message bubbles. Three short bubbles sent in
one minute are one turn. Multiple unanswered member messages reduce the next
sequence, never increase it.

## What each message earns

**A follow-up needs a reason to exist, and "just checking in" is not one.** Before one is
drafted, find three ideas worth telling this client, one per draft, from these sources in order:

1. **Their own business, when it has a website.** Find the business from the job post, the
   room name and the thread, then read its website and Google Business Profile. Build each
   idea on what you saw: a phone number with no booking link, a form that breaks on a phone,
   reviews nobody answered. Never a person's private profile, and when you are not sure
   the site is theirs, treat it as no website.
2. **No website: their niche.** Research businesses like theirs online, then build the ideas
   from the service the member sells, the conversation, what you found and the niche's normal
   conventions. Offer each as an idea, never as a fault found on their business.
3. **A relevant result:** one line from the evidence sections of `context/me.md` that answers a worry they voiced.
4. **A graceful close**, on the last day only: you stop writing until their timing changes.

**Five minutes on their business, then three things and stop:** their name and problem, the
one idea, the call offered and never pushed. "Hi Sarah, one more idea on your missed calls:
text every missed caller a booking link, not just a sorry. Happy to show you on a quick call
if it helps." Every message is written with [persuasion.md](persuasion.md) open and as the member.

**The receiver test: four yeses or it does not go out.** Read each draft as the client, who owes
the member nothing: can they use it without replying or hiring, would it stop making sense under
another client's name, is it new to the thread, does it give more than it asks? A no means another
angle, named in the report and never scored. With none left there is no message: say so and move the date.

## Workflow

Turn the current pipeline and fresh conversations into today's follow-up queue.
The member starts every run. The run decides and drafts; a draft only leaves on
their yes to that one message.

### Start with current evidence

Read `data/sync.json` and run
`python3 code/pipeline.py summary`.

If today's sync is missing or any relevant thread is older than 24 hours, follow
`.claude/commands/dashboard.md` Step 1 once before reviewing. Call the connector as
`references/upwork.md` describes. Never poll or read every historical room.

Review jobs in `replied`, `call`, `offer` and `won`. An `applied` proposal without a room
cannot receive a message, so leave it waiting without a task, reminder or draft.

### Decide from the conversation

For each job, read the pipeline record and the full saved thread oldest first.
Use the status, `awaiting_reply_from`, last meaningful message, explicit dates,
client engagement and consecutive messages from the member. Apply the lane,
cadence and stop conditions above.

Stop when the thread is weak, the client moved the conversation elsewhere or
another message would add no reason to answer.

Keep an existing plan; never restart a finished or stopped sequence unless the client returns.
For a new sequence, write the decision only through:

`python3 code/pipeline.py follow-up <id> plan --lane <lane> --due <date> --reason "<conversation-based reason>"`

Clear a sequence when a stop condition applies:

`python3 code/pipeline.py follow-up <id> clear --reason "<why>"`

### Draft only what is due

For every sendable lead due today or earlier, follow `references/copy.md` and
Step 5 of `.claude/commands/dashboard.md`. Save three drafts, A, B and C, one idea each, to
`jobs/<id>/replies.json` and run `python3 code/replies.py check <id>`. The member picks one.

Each follow-up carries the reason found under "What each message earns". A pure
"just checking in" message is not a draft.

Report each due lead's decision and reason in chat. The cockpit shows each lead's
next action, waiting date or Parked state in its existing board and list.

### Report

Use the repository's completion report. Lead with the number due now and name
the strongest opportunity. Then run `python3 code/pipeline.py follow-up <job id> sent`
for each message that actually went out, whether it left from here on the member's
yes or they sent it on Upwork and said so. The sequence advances on arrival, never
on the draft. End with the exact Upwork call count.

### Self-improvement

When the member corrects a cadence decision or a follow-up wins a reply, ask
whether to keep the lesson. If yes, record it against that job with
`python3 code/pipeline.py note <job id> "<the dated observation>"`, where the
next run will find it. Change the intervals in this file only after two
independent examples support the same default.
