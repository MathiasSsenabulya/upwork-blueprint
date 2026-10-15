---
description: Finds the Upwork jobs worth your Connects right now, scores them against your finished profile, and puts the best into your pipeline and dashboard.
argument-hint: "[focus: filter | filter <settings copied from the dashboard> | recommended | tracks | recheck | skip <job id> <reason>]"
---

# /find-jobs

**Before anything else, read [references/upwork-compliance.md](../../references/upwork-compliance.md) in full.** Where a step below reads looser, that file wins.

Before starting, read and follow [analytics capture: find-jobs](../../references/analytics-capture.md#find-jobs), including its shared rules and replacement steps.

Looks at what was posted since the last run from two directions: Upwork's recommendations and the member's own search themes. Code counts client, budget and freshness signals; Claude judges fit, out of ten, and that is the score. Runs only when the member runs it.

Read first: [references/upwork.md](../../references/upwork.md) for what is allowed and what the connector gives you, [references/jobs.md](../../references/jobs.md) for where the work comes from and what it pays, `context/me.md`.

## Taking a lead off the list

`skip <job id> <reason>` does only that: it calls no Upwork tool and runs no search. Step 7 asks the same question for the current run's leads; this writes the same record later. The X on a dashboard row skips a lead too, in one click and without a reason: use this command when the next search should learn why.

Run `python3 code/pipeline.py get <job id>`. Only a Not applied lead (status
`new`) can be skipped. A lead further along moves through `/dashboard`, so say that
and stop. Without a reason, ask with one single choice (budget, scope, tool, client) and
wait: a useful reason names the fact that rules the job out, never a mood, and a typed
detail is saved with the pick ([references/copy.md: How to ask](../../references/copy.md#how-to-ask)).

Then `python3 code/pipeline.py set <job id> skipped --note "not a fit: <reason>"`.
Keep the prefix. `python3 code/jobs.py rules` counts a reason only when the note
carries it, so a note without it takes the lead off the list and loses the lesson.

Report one line: the job title, the reason as saved, and that the lead left the
cockpit list. End with `Upwork calls: 0`, and do not continue into Step 0.

## Step 0 · Files, connector, window

Run `python3 code/workspace.py`, `python3 code/pipeline.py prune` and `python3 code/pipeline.py reset-search` (yesterday's unused leads expire, with skip reasons kept), then `list_accounts` (if missing, walk the member through connecting as CLAUDE.md says and stop). Then `python3 code/jobs.py window`: the hours since **the last run rather than the last saved lead**, with a two-hour floor and 24-hour ceiling. A first run looks back 24 hours. `jobs.py clean` writes the stamp even when nothing was found, so the run must finish for the next one to narrow.

## Step 0b · Is this the first run, or a run with a direction?

If `python3 code/context_check.py --status` says `untouched`, stop and send the member to `/about-me`.
Look at `context/me.md` under "Job search tracks". **No tracks means the first run**:
it finds which searches are alive first, then hunts the best ten in the same run.
Saved tracks mean a later run even before any application. Name the mode in one line.

**The first run explores first.** If what the member sells matches a ready-made lane in [references/jobs.md](../../references/jobs.md), offer that lane's terms and let them cut what they cannot deliver. Otherwise build ten to twelve candidate terms from `context/me.md` across the four branches: tools, roles clients hire for, problem words, and business models (services, software, ecommerce), never a single trade. One lane at a time, never two. One call per term, `limit` 10, `sort` `recency`, and **no window filter**, since the point is density. Measure with Step 3a and report per term its Connects cost, what postings pay against the member's own rate in `context/me.md`, and how many ask for entry level.

Save three to five surviving terms under "Job search tracks" in `context/me.md` as `- Theme: term · term`, with verdicts and dates in prose outside that list, and name the lane the evidence supports. **Then the same run goes on to find jobs** (12 October 2026: a first run that showed no jobs read as broken). Tell the member in one line that the first run takes a bit longer because it also checked their searches: how fast new jobs arrive, what they pay and what a bid costs. Continue with Step 1 on the saved tracks; the responses already saved for the kept terms count as their first page in Step 2. With no surviving terms, run `python3 code/pipeline.py prune` and `python3 code/jobs.py clean`, report the measured terms and `Upwork calls: N`, name `/about-me offer` next, and stop.

**Every later run exploits.** It runs the kept tracks, pages the dense ones, applies the
lessons from Step 3b, honours the window from Step 0, and tests at most one new candidate
term per run so a bad guess costs one call, unless the run comes up short of the target (Step 6b). A term that returned nothing twice gets
removed from `context/me.md` with a line saying so.

## Step 1 · Invitations first

Call `list_freelancer_proposals` action `invitations` once. Open invitations are the warmest leads and go to the top of the report. For each one not yet in the pipeline, fetch the job with `find_jobs` action `get`, add it with `python3 code/pipeline.py add --file -` (id, title, url, budget, job_type, client, posted_date, `found_via` set to `invitation`), then store its details as Step 6 does. The member answers on Upwork; this command never accepts or declines. No invitations: say nothing and continue.

## Step 2 · Search, two directions

Save each response's `jobs` list to `data/search/<name>.json` as `{"jobs": [...]}`, every job with its fields as returned. The file name becomes the job's "found via", which is how weak tracks get noticed later.

0. **The filter starts as the one the series teaches, and the member keeps it or changes it, once, before a single call is spent.** The starting filter (12 October 2026): at most 50 proposals, posted within 24 hours, full-time roles hidden, clients rated under 4.0 by three or more freelancers hidden, unverified clients shown and marked, no pay floors. On the first run, with the `filter` focus, or whenever a line below is still unanswered, run `python3 code/jobs.py filter`, show its two lines and ask one single choice: keep it · change it. On keep, run `python3 code/jobs.py filter bids=50 posted=24h full-time=hide rating=4 unverified=show hourly=none fixed=none` so every line is answered and the question never returns. No limit is ours to set for everybody (a fixed budget that is small in one country is a good week in another), so on change, point to the dashboard's Job filter menu, which builds the settings as one line to paste, or put the seven lines as single choices ([references/copy.md: How to ask](../../references/copy.md#how-to-ask)), your recommendation for this person first, with half a line of why:

   - **Unverified clients:** show them, marked · hide them. An unverified client is often simply a first-time hirer who adds a card when they hire. Shown, the lead carries a mark and the rule that nothing starts before payment is verified or the milestone is funded.
   - **Full-time roles:** hide · show. Hidden unless the member wants a job more than projects.
   - **Oldest posting:** 24 hours · 12 · 6 · 48. Fresher means fewer proposals ahead of them.
   - **Lowest client rating:** hide clients under 4.0 with three or more reviews · under 3.0 · no floor.
   - **Hourly pay floor:** none · 60% of their rate · 80%.
   - **Fixed-price floor:** none · about ten times their hourly rate · $250 · their own figure typed.
   - **Proposal cap:** 50 · 20 · 5 · none.

   **What you recommend depends on what they have earned on Upwork**, read from the profile or from their Upwork status answer. Under $1,000 earned: the starting filter as it is, with no pay floors and unverified clients shown, because the first reviews are worth more than the first dollars. From $1,000: the 60% hourly floor and a fixed floor near ten times their rate. A high rate with proof: 80% (the tiers in [references/jobs.md](../../references/jobs.md); reasoned, not measured).

   Then list the search tracks as checkboxes, ticked meaning searched today, one line per track with its source: their own file, the catalog in jobs.md, or a skill name harvested from the last run. A missing term is typed. Wait for the answers: a wrong term or limit costs the member a day of leads.

   Save the picks in `context/me.md` as `**Unverified clients:**`, `**Full-time roles:**`, `**Oldest posting:**`, `**Lowest client rating:**`, `**Lowest share of your rate:**`, `**Smallest project worth taking:**` and `**Maximum proposals on a job:**`; "none" switches a limit off, and `python3 code/jobs.py rules` reads them. A later run prints the saved filter in two lines and asks nothing, and `/find-jobs filter` rebuilds it.

   **A filter pasted from the dashboard is already the member's pick.** The dashboard's Job filter menu builds one line, such as `/find-jobs filter bids=50 posted=24h full-time=hide rating=3 unverified=show hourly=none fixed=none`. Run `python3 code/jobs.py filter <those settings>`: it checks every setting and writes the lines above into `context/me.md`. Print the two lines it answers with, ask nothing more about the filter, and search with it. When it refuses a setting, show its message and stop: nothing was saved. A limit whose figure is unknown prints as `LIMIT OFF` in the candidate step: name it out loud.

**When the member sells something the catalog does not cover**, build the list with them from the four branches, then harvest Upwork's own wording from one broad search (method in [references/jobs.md](../../references/jobs.md)). Save what they confirm under "Job search tracks" in `context/me.md`.

1. **Upwork's recommendations:** when the connector exposes it, use the documented but untested `find_jobs` action `smart_search`, `mode` `most_recent`, `days_posted` the window in days rounded up and `verified_payment_only` true unless the member's filter shows unverified clients. Page with `cursor` set to the previous `pageInfo.endCursor` while `pageInfo.hasNextPage` is true, at most 4 pages. Save as `recommended-1.json`, `recommended-2.json` and so on. If the action or documented response shape is absent, report that evidence gap and continue with search themes rather than guessing.
2. **Your search themes:** run `python3 code/jobs.py rules`. Its `themes`
   are the member's personal configuration from `context/me.md`. Each theme
   groups useful variations and tool names into one semantic query. For every
   theme, call `find_jobs` action `search`, `query` the emitted `query`, `sort`
   `recency`, and `verified_payment_only` true unless the member's filter shows
   unverified clients. **Page until the window is
   covered**, not to a fixed page count: keep setting `cursor` while
   `hasNextPage` and the page's oldest job is still inside the window, and stop
at the page that crosses it.

   **Send the member's own limits with the query, so the pages that come back are
   pages worth reading.** The search filters are free and server side:
   `proposals_max` for the competition ceiling, `budget_min` for fixed work,
   `rate_min` for hourly, plus `experience_level`, `job_type` and `workload`
   where the member has named a boundary.

**The window decides the page count.** Twelve pages is the runaway stop: report the term as denser than one run can reach and offer to split or narrow it with a filter. Say how many pages a term took, since that is the density measurement. Save as `query-<slug>.json`, using the emitted `slug`. Never split the grouped query into separate calls.

   If there are no themes yet, propose three to six from the member's services,
   profile skills and proof. Use `- Theme: term · variant · tool` lines, each starting with the dash because `jobs.py rules` reads no other line, write
   them under "Job search tracks" in `context/me.md`, and say so in one line.
   Do not add a service merely because a tool exists; the member must actually
   want that work.

3. **The business model, never the trade.** One profile sells one service to whole markets: services that live on calls and bookings, software that lives on trials and demos, ecommerce that lives on sales. A track may carry a market word beside the service ("Google Ads lead generation", "Google Ads ecommerce", "Google Ads SaaS") and never a trade ("dental Google Ads"): whoever understands landscapers understands plumbers. A track in `context/me.md` that names a trade gets widened: say which one and to what, and rewrite the line on the member's yes. An old `Industries you want to work with` line is ignored; nobody is asked it any more and it never narrows a search. Save as `market-<slug>.json`.

4. **The client's own tools, the quiet half.** Search the platforms the member can work with even when the posting never says "automation": Shopify, Salesforce, Monday, ClickUp, Zoho, Pipedrive, Google Calendar, Gmail, Zoom. Propose two or three such tracks from the member's own stack, mark them in `context/me.md` like any theme, and save as `query-<slug>.json` so the funnel shows which branch paid.

Default to broad themes and score after retrieval. Do not add a proposal-count
or budget filter unless `context/me.md` records that boundary as a member choice;
filters remove jobs before anyone scores them.

**Never disqualify a client on a thin signal** (no spending history, low average spend, few reviews; see references/jobs.md). Only the posting's own text fixing a low budget and a deadline together disqualifies. Honest reviews are the one signal worth reading closely.

## Step 3 · Count

Run `python3 code/jobs.py candidates data/search/*.json --window-hours <window>`. It drops what you already applied to, unverified clients and anything outside the window, merges duplicates across searches, skips jobs already in your pipeline, and prints each candidate with its client, budget, competition and points for trust, deal and recency.

**The pool comes before the pick: at least 100 different postings.** The ten leads are the top of a wide net, never the best of thirty rows. The last line of the candidate step says how many different postings this run read. Below 100, climb the ladder of Step 6b now, before any fit is judged, and run this step again; 100 is the floor, and more is better.

## Step 3a · Measure which terms are worth their calls

Run `python3 code/tracks.py measure data/search/*.json`. Per term it reports the hours its ten newest postings span (the density: a live term gives ten in eight hours, a dead one reaches back three weeks), how many state a rate, the median proposal count and how many clients are payment verified. The verdict decides the next run: dense terms get a call and a page every run, steady terms one call, thin terms a weekly look. Say which terms changed category and drop a term that returned nothing twice.

## Step 3b · Apply what your own pipeline has taught

Run `python3 code/learn.py report`. It counts what happened to applied leads by search branch, client country, spending history, job type, requested level and the member's score band.

Two lines work from the first run because they count decisions. **Per search branch**: how many candidates reached the pipeline; a branch that keeps producing and never passes one is a keyword list to drop. **The disagreements**: leads the score let through and the member turned down, with reasons; weigh one of those above ten counted outcomes.

**Broad first, a niche from evidence later.** A new member casts a wide net across business models to learn what they like, what gets answered and where the money is. So before five won jobs, never suggest a niche. From five won jobs on, say in one line where the wins and the money cluster, by business model and by trade, read from the won leads. Between five and twenty, when one cluster clearly carries most of both, recommend narrowing to it as a single choice: lead with it (a track for it, and `/profile` gets the hook), or stay broad. It is always the member's pick, and their own numbers are the only argument.

Outcome lessons wait for a sample: below eight applications in a bucket nothing is weighted. Past it, `python3 code/learn.py lessons` writes `data/lessons.json`. **A lesson never moves a score** (12 October 2026): the score says how close a job is to the member's work and nothing else. Say in the run which track, country or job type is getting replies and which dimension is still too thin, so the member can weigh it.

## Step 4 · Judge fit

Run `python3 code/jobs.py lessons` first: the member's past decisions, including
every reason saved with a skip. Use relevant reasons to
calibrate fit and explain their effect in the candidate's rationale. A bare
"not a fit" is not evidence of a particular budget, market or tool preference.
Treat one rejection as specific to that job; repeated reasons can guide ranking,
but never invent a blanket exclusion or silently rewrite `context/me.md`. Only
explicit member boundaries there may remove jobs before scoring. Automated
"cannot apply" skips describe eligibility, not the member's taste.

Also read `performance` from `python3 code/jobs.py rules`: saved leads, applications, conversations, wins and disqualifications by search theme. Prefer themes that produced conversations or wins when choosing borderline jobs to open; repeated disqualifications with the same reason are named in the rationale for that pattern. Never disable or rewrite a theme without the member's explicit decision.

The member's own history outranks any sentence in `context/me.md`: it is what they did, and the only thing that can tell the score it was wrong.

**Every fit names its comparable case.** The rationale says which past lead this job resembles and how it ended ("like the pet grooming lead that replied"). A rationale that only asserts fit is taste. With no history yet, say so plainly and score against `context/me.md` alone. Three turn-downs with the same reason go into the rationale of the fourth job of that pattern, so the member sees it before spending Connects.
Then answer four yes-or-no questions for every candidate, from `context/me.md`.
**The score is how close the job is to what the member does, and nothing else**
(12 October 2026). `jobs.py score` adds the answers up, so the same job scores the
same in every run and the member can see why.

- **Is it a service they sell?** Yes makes it a 7. No keeps it off the list, whatever
  the client or the budget pays.
- **Is it their main offer?** The service they lead with and want more of. Plus one.
- **Does it name tools they use?** A tool from their own stack, in the posting. Plus one.
- **Do they have a result or a sample project like it?** From their evidence sections
  or their portfolio. Plus one.

Client, competition and budget are not in the score. The candidate step lists them as
doubts and the dashboard shows them in their own columns, where the member decides.

**A trade never changes an answer:** a chiropractor's ads are a dentist's ads and a
roofer's are a plumber's, so a result from one trade counts for another in the same
service. Tools and proof add their point, but never turn an unrelated job into their service.
Traps that look like a match and are not: ranking or result guarantees, bought
links or reviews, work outside the services the member sells, open-ended
account-manager roles, a full-time employee disguised as a contract, and
anything the member ruled out in `context/me.md`.

**A pool of a hundred or more is judged in two speeds.** Every candidate gets the service answer. Only a yes gets the three checks and the full entry below; a no gets `"service": false` and a rationale of a few words, which is the reason the decision log keeps. Writing three sentences about a lead nobody will see is where a wide search would turn slow.

Write `data/fit.json`: per job id `{"service": true or false, "checks": {"main_offer": true or false, "tools": true or false, "proof": true or false}, "rationale": "<what the score bets on, in one sentence of at most 15 words>", "summary": "<what they want built and the one thing that makes this job distinctive, in two or three concrete sentences>", "headline": "<who wants what, one sentence of at most 14 words>", "trap": "<only when one applies>"}`. The cockpit list shows the headline whole, so it names the client and the concrete outcome, never a category label. The rationale never repeats what the card already shows (budget, client rating). The summary must let a member explain the job without reopening the posting; never reduce a multi-part build to a category label.

## Step 5 · Score and log

Run `python3 code/jobs.py score`. It adds the answers up: 7 for their service, plus one for each check, 10 at most. It logs every job that scores at least 7, caps any job you named a trap at 6, and prints each score with the checks behind it; the doubts ride along on the record for the dashboard's columns and take nothing off. Everything turned down goes to `data/decisions.jsonl` with the reason, which the next run learns from. Tell the member the score and its checks, in those words.

## Step 6 · Open the ten you will show

**Open exactly the leads that will reach the member**, one at a time, highest first: the ten of Step 7, plus a replacement for every one the full posting disqualifies, until ten stand or the bench above grade 7 runs out. An unopened lead hides its mandatory opening phrase, screening questions and self-capping budget, which kill an application after the Connects are spent. Ten one-at-a-time calls is not the pattern Upwork flags; fetching the whole candidate pool would be.

For each of them: `find_jobs` action `get` with the job id. Save to `data/details/<id>.json` these parts of the response, as returned: `connects_cost`, `can_apply`, `activityStat`, `preferred_qualifications`, `client_record`, `contractTerms`, `clientCompanyPublic` and the full `description`. The last two carry the experience level, engagement type, client city and timezone that `jobs.py detail` reads.

After reading that full description, add a `brief` object to the same file:

```json
{
  "outcome": "One sentence of at most 20 words: what should exist when the work is done and who uses it.",
  "scope": ["Two or three deliverables, at most ten words each."],
  "requirements": ["Only hard must-haves or application instructions, at most two, ten words each."]
}
```

Use the client's facts, not guesses. Do not mix fit, competition or sales advice into this brief; those have their own places in the cockpit. Then `python3 code/jobs.py detail <id> data/details/<id>.json`. It stores the brief, Connects price, competition, hiring progress and full posting. Only a new job with `can_apply` false is skipped automatically. Hiring progress and unmet preferred Job Success or earnings are advisory: a job may hire several people, and a preference is not an eligibility block. Never fetch details for a whole list: that is the request pattern Upwork flags as scraping.

Now answer the four questions again from the full posting, including every mandatory
requirement. Replace its entry in `data/fit.json`, then run
`python3 code/jobs.py reassess <id>`. This replaces the snippet-based score and
closes the lead when the full posting falls below the same fit or score gate.
Never let the snippet score survive as the final assessment for an opened job.

Write the outcome in plain language: who uses the finished work, what happens
for them, and what changes. Expand shorthand such as "membership automation"
into the actual behavior from the posting. A member should be able to explain
the job aloud after reading it once. Brevity wins: the side panel shows the
scope and requirements as bullets of 50 words in total, and the posting itself
is one click away on Upwork.

**Name the client's industry first, in the headline and in the first sentence of the outcome**: "A dental practice wants its GoHighLevel CRM cleaned up and automated", never "A business wants...". Take it from the posting (the client's own words, company profile, examples), never infer it from the tool they use. When the posting does not say, write "industry not stated", never a plausible guess; that blank is itself worth seeing.
The list uses this outcome, or the saved `summary` when no full brief exists.
Keep both focused on the requested work. Put proof fit, competition and advice
in `rationale`, not in the job description. The sidebar shows that assessment.
To clarify an existing member-written summary, use
`python3 code/pipeline.py describe <id> "Plain-language summary"`, and for the
list's one-sentence headline `python3 code/pipeline.py headline <id> "<sentence>"`.

## Step 6b · Short of the target: widen the net, in order

Six good leads when the member asked for ten is a search that stopped early. The same ladder serves two checks: the pool of Step 3 (at least 100 different postings read) and the target after Step 6 (ten leads standing). Climb it one rung at a time and stop when both hold. Say the call budget before the first rung: **at most 30 search calls in the whole run**, ten rows each, never the same query twice.

1. **Further back.** If this run's window was shorter than 24 hours, run the same tracks again over the full 24.
2. **Deeper.** Page the tracks that were still returning fits when they stopped, up to the twelve-page stop.
3. **Wider.** Run what this member can deliver and this run did not search: the other business models for their service ("Google Ads ecommerce", "Google Ads SaaS"), the catalog terms of their branch in [references/jobs.md](../../references/jobs.md), then the next branch they said they can deliver today. One page per new term, five new terms at most.
4. **Older.** Postings from the last 48 hours that still sit under the member's proposal ceiling. Mark each one "older than a day": more people have seen it.

Every new candidate goes through Steps 3 to 6 like the first ones. **The gate never moves:** a lead below it is not a lead, whatever the count is, and nothing is padded in. The budget is a ceiling, not a loop: when it is spent the search ends, and Step 7 says how many stand and what would have found more.

## Step 7 · Close

1. `python3 code/pipeline.py prune`, then `python3 code/jobs.py clean` (deletes this run's raw responses).
2. **Show the daily target, and the bench is everything else that passed.** The target
   is ten unless `Applications per day` in `context/me.md` says otherwise. Show that
   many, numbered, each one line: who wants what, the grade, and what applying costs in Connects.
   Within a grade the freshest goes first, and a lead under an hour old says its age: being early
   is the one lever on replies with a large measurement behind it. Behind them
   stands every other lead that passed the gate, in rank order, which is what
   `python3 code/pipeline.py list` already prints. Open invitations come first, before the ten.
3. Ask once which of the leads you showed are a no, as checkboxes over the numbered
   leads with "keep all of them" among them, then why in one more call: one single
   choice per lead turned down (budget, scope, tool, client), a typed detail kept with
   it. Take any answer, including none, and record each with
   `python3 code/pipeline.py set <id> skipped --note "not a fit: <reason>"`. Keep the
   prefix, because `python3 code/jobs.py rules` counts a reason only when the note
   carries it. A reason names the fact that rules it out, such as budget, scope, tool
   or client. This is the half of the record that needs a person, so it is asked once,
   here, and never chased. A lead the member rejects later takes the same route through
   `/find-jobs skip <id> <reason>`.
When the member turns one down, name the next one in the same breath, so the list is ten again before they ask, while the bench holds. **The bench floor is the gate itself**: a lead below the gate is never offered as a refill. The bench is good for today only, since tomorrow's window disqualifies it. The complete scored list lives in the cockpit.
4. **Say it when ten is not there.** After the widening of Step 6b, fewer than ten at a 7 or better is a result, not a failure to hide: report how many there are, which rungs were climbed and the cause (too few dense tracks, limits too tight, a quiet day, or a member with empty evidence sections, where a direction still two lanes wide scores honest fits at 7 and 8 and the gate eats them). Never pad the ten with leads the score turned down, and never lower the gate to fill a row.
5. **Name the day's Connects bill once.** Ten applications cost what the ten jobs cost,
   measured from each `connects_cost`. Call `get_freelancer_dashboard` action `check`
   once for the Connects balance, and include this call in `Upwork calls: N`. One
line, no advice unless the balance runs out before the ten do.
6. **Say once how to be first.** A run only sees what was posted before it started, so the fastest route is the member's phone: save today's tracks as searches in the Upwork app with its job notifications on, and when a posting looks right, type `/proposal <its link>` inside five minutes. That takes the fast lane: the letter first, the page after.
7. Put the list in front of the member. A dashboard of this repo already running: say a reload shows the new leads. Otherwise run `python3 code/cockpit.py --no-open` in the background, wait for "Dashboard running" and open the exact URL it prints (`open` on macOS, `xdg-open` on Linux and WSL). It only shows the list: no sync, no drafts. No Node.js: the ten stay in the chat.
8. Use the compact completion report from `CLAUDE.md`. Next step: `/proposal <id>` for the first lead on the list, or the cockpit. Every lead shown has its full posting saved. End with `Upwork calls: N`, measured, never an estimated range.
