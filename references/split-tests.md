# Split tests

The top mover's change gets tested against the old way, and the winner becomes the
default. 80% sure is enough: time is money, and a member who waits for 95% quits
before the result lands.

## Rules

- One test at a time, always on a mover of the stuck stage. /analytics names the 1 to 3 changes that get 90% of each stage's result; the highest one on the stuck stage that can be tested is the test.
- A is the old way. B is the whole new version: every fix of that stage together, named in one line.
- Big swings first: a new proposal, a new video, a new bio, a new close. Never a one-sentence test.
- What research already settles is just done, not tested: speed to lead, volume, a bio video, plain words (grade 7 or under), no off-platform links.
- Code tags each lead and reads the result from the pipeline. Never count by hand.

## What to test, per stage

**Profile.** One profile at a time, so it runs before and after: the 28 days before the change are A, everything after is B. A win is a reply within 7 days. Change everything at once on day one, then leave it alone.
- Bio: the formula against the current one
- Title: a result for a kind of client, against a job title
- Bio video: talking to camera, against showing a past client's result on screen (a bio video is required either way)
- Portfolio: pieces that match the jobs bid on, with images or video, against the current set
- Available now badge on, against off

**Proposals.** A or B per proposal. A win is a reply within 7 days. Code checks each sent copy.
- Structure: proof, result, offer and a question, against the current letter
- Proposal video: their own site on screen, against no video or a talking head
- Offer: a free first step or a guarantee, against none

**Messaging.** A or B per lead. A win is a call booked within 14 days.
- Follow-up rhythm: day 3 and 7, against every weekday for a week. The pipeline schedules each quiet lead's follow-ups by its side.
- Reply: a 60-second video reply, against text
- Call ask: an Upwork meeting invite straight away, against asking which of two times works
- Answer one question then ask for the call, against answering everything in writing first

No booking link of the member's own before a contract: Upwork treats it as taking the client off the platform.

**Calls.** A or B per call, given in /sales-call-prep. A win is an offer or a deal within 14 days. Each call's grade says which way the call actually went.
- Close: send the offer on the call, against booking a second call
- Proof: screen-share a past client's results, against talking through them
- Price: say it on the call, against sending it in writing after
- The piece before hiring: a free audit, against short research, against a paid first step

Calls are few, so a call test takes weeks: five finished calls a side before any call.

**Offers.** A or B per offer, given in /sales-call-proposal. A win is a deal within 21 days.
- One price, against three options
- A small paid first milestone, against the whole project
- A guarantee, against none
- Price: a test of rate lives here, where a win is money, not at the profile, where a win is only a reply

## The loop

Hands-off: the member only sends what the commands write.

1. **Start.** /analytics saves each stage's movers with `diagnosis.py save`; the mover carrying `test` starts it. By hand: `python3 code/split_test.py new <stage> --a "..." --b "..." --b-checks <marks> --mover "<title>"`. A follow-up rhythm adds `--a-days 3,7 --b-days 1,2,3,4,5`.
2. **Use.** The command that writes the piece (`/proposal`, `/dashboard`, `/message`, `/sales-call-prep`, `/sales-call-proposal`) runs `python3 code/split_test.py assign <id> --stage <stage>` first and writes to the side it prints. A profile test has no assign. A rhythm test assigns when the follow-up is planned.
3. **Check what was sent.** Code reads each sent proposal and reply against `--b-checks` (proposal: `question,offer,video,no_filler,own_words`; reply: `question,call_times`). A call's grade records which way it went. A lead sent differently from its side is left out and counted.
4. **Call it.** Every /analytics run reads `python3 code/split_test.py status`, and calls it without asking:
   - **ship B** at 80% or more, five finished leads a side: `python3 code/split_test.py ship B`
   - **keep A** at 20% or less: `python3 code/split_test.py ship A`
   - **keep going** in between
5. **Keep it.** The winner goes under `## Split test winners` in `context/me.md`, and a rhythm on `**Follow-up days:**`. Every command reads that file, so the winner is the default from then on. The next test starts from that week's movers.
