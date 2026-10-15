---
description: Writes your Upwork profile from your own facts and three role models, checks it, and puts it live after one yes. Every number in it is backed by your own evidence.
argument-hint: "[title | overview | skills | portfolio | video | fields]"
---

# /profile

**Before anything else, read [references/upwork-compliance.md](../../references/upwork-compliance.md) in full.** Where a step below reads looser, that file wins.

Before starting, read and follow [analytics capture: profile](../../references/analytics-capture.md#profile), including its shared rules and replacement steps.

Follow `references/copy.md`, and put every question as a pick ([references/copy.md: How to ask](../../references/copy.md#how-to-ask)). Sell only the member in `context/me.md`; import no outside voice or identity. Most members have no live profile: write one from their facts; a live profile adds the Step 2 review. **Three things come out of a run:** `profile.md`, the paste-ready source; `profile.html`, the same draft as a page in the house look; and, once the critic would choose it over the next nine and the member says yes, the profile on Upwork itself. The deliverable is the written profile, never a report on an old one.

Read first [references/profile.md](../../references/profile.md), [references/persuasion.md](../../references/persuasion.md) (why a line makes a client act), the profile sections of [references/upwork.md](../../references/upwork.md) (what the connector may write), then `context/me.md`.

**Focus:** $ARGUMENTS writes only that section of `profile.md`. Every run writes something. **`video`**: Steps 1, 4, 5 only; script from `context/me.md` and existing `profile.md`, no live read, no role models.

## Step 0 · The connector

1. Run `python3 code/workspace.py`.
2. Call `list_accounts`. If the Upwork tools are missing, walk the member through connecting per CLAUDE.md and stop; they rerun `/profile` after the restart.
3. Take the Freelancer account's `org_uid`, never write it to a file; if several, ask which.

## Step 1 · Read your facts

`context/me.md` holds background, offer, terms and provable results (`/about-me` writes it; this command repeats none of that interview). Build everything from its recorded direction (lead branch, offer, audience, country). Never reopen it or suggest another lead branch; a proof/direction mismatch is one line under "Decide first". Ask only for role-model addresses, the four picks of Step 4, the profile fields nobody has told you (Step 4b), the rate and a yes per field.

Run `python3 code/context_check.py`. Open questions never stop you: draft from what exists and list every gap under "# Decide first" atop `profile.md`. **One exception: a line naming the proof interview stops the draft.** Say which questions are open and send the member to `/about-me proof`; a question answered "none" is answered. If `python3 code/context_check.py --status` says untouched, `/about-me` comes first.

**Use the member's own concrete figures, with or without a place to check, worded as their claim; invent none.** An entry still marked pending was pulled from elsewhere and waits for their yes. The gate checks every number against `context/me.md`. A claim without a figure stays out. With no usable result, lead with offer and background (normal for a first profile).

## Step 2 · What is live, if anything

Call `get_profile` action `get`, save as returned to `data/profile.json`, then `list_highlights` to `data/highlights.json`; skip both if the files are under 24 hours old.

**No or nearly empty profile** is a normal start: say so in one line, skip the rest of Step 2, let Step 5 list what to create. Never invent a score or infer experience.

**With a live profile**, measure and judge it:
- Run `python3 code/profile_checks.py data/profile.json data/highlights.json --json`. The script decides mechanical pass or fail; never overrule it, say in chat if a result looks wrong.
- **Completeness**: list every missing field with its percentage (`references/profile.md`), cheapest first. Only here may you claim a complete profile ranks better.
- **Client filters** (`references/profile.md`): check all six; an empty one fails silently.
- **Judge:** do title, overview, skills, portfolio tell one story; is the result clients care about inside the first 250 characters; does a claim contradict the aggregate in `data/profile.json` (a badge or count Upwork denies is the costliest error); what could the member add that nobody in the lane does (a price, a "not for you if").

**Job Success Score and intro video** come from `context/me.md`; never estimate an unanswered field.

## Step 3 · Skills, role models and rate

**The skills clients type: harvest far more than you need, then cut.** The connector has no skill list to browse, so the names come from postings and profiles. Say the call budget first: up to six `find_jobs` action `search` calls, `sort` `recency`, `limit` 10, one per angle of the recorded direction: its main tool, the role clients hire for, two neighbouring tools or services from the member's branch, and two problem phrases in the client's own words. Count how many postings carry each name in their `skills` arrays (Upwork's spelling, the client's vocabulary), and add every skill on the role models' profiles and on the member's live profile. That pool is some sixty postings and usually forty to eighty names. **Then cut to the best 20:** only what the member can truthfully deliver from `context/me.md`, ranked by how many postings carry it, the direction's main tool first. Keep the next ten as a bench. The same count orders the title's keywords. Note skills the live profile lacks and any it carries that appeared in no posting.

**Three role models, before any draft.** Ask for the addresses right after the plan so the member can fetch them while you read the skills; write no draft until they are in or declined (they give hook, structure, close, lengths). The connector cannot search freelancers, so the member adds a client profile to the same login (Account Settings, no job posted) and uses Upwork talent search with their country, the Top Rated filter and the direction's keywords, favouring high earnings, many finished jobs, recent work. They paste three to five addresses (the `~` is the key) plus two or three newer freelancers from their country with few reviews. Ask with a single choice (I will paste them, or go on without); the addresses themselves are pasted. If they decline, go on without. Read each in full with `get_profile` action `get` and its `profile_key` (title, whole overview, skills, portfolio titles, employment, rate, earnings, jobs); rank by success (earnings bucket, then jobs and reviews), pick the three closest by shared skills and rate band, name the criteria, and say job success score and hours are not visible. Give four chat lines each: title, how the overview is built from open to close, skills and rate band, one thing to borrow, with URL. Take structure only, never sentences (copying gets flagged). Keep no profile text in any file, only the numbers below.

**The rate.** After the role models, recommend one starting rate, labelled a recommendation. **A profile with no review and no badge starts at the entry price:** about $20 an hour in a developed country (the US, Canada, the UK, western Europe, Australia and the like); elsewhere 60 to 75% of the median hourly rate in the postings of their branch (the ten postings above, with n and today's date), which lands near $15 to $20 for these branches, checked against what the newer profiles from their country charge. Not lower: a $5 to $10 rate fights for the smallest slice of postings and stays on the profile as a public anchor. Never recommend the posting median or more to a new member: the middle band gets the fewest replies, and clients filter by rate, so a profile above their band is not shown at all. Show the market figures as where the rate is heading and say the entry price exists to win the first reviews. **Say how it rises:** after every two finished clients at the current rate, raise the profile rate before the next application, which never touches a running contract. Staying low is the mistake, not starting low. Experience and proof from outside Upwork do not raise it: clients price an empty profile as an empty profile, so that proof belongs in the overview, not in the rate. With reviews or a badge on the profile, recommend from the hourly ranges and fixed-price medians in the ten postings (with n and today's date), newer low-review profiles' rates, [references/jobs.md](../../references/jobs.md) and the member's proof in `context/me.md`. Never from the Top Rated role models. Label measured versus guess and carry the question "what would you actually quote?" into the live-preview message of Step 6 instead of a separate turn. Once they answer, write it as a number (range fine, their first-quoted figure first) into the `**Hourly rate:**` line of `context/me.md`: `/proposal` prices from it and `data/profile.json` is deleted after a day. Never ask for a smallest project.

## Step 4 · Write profile.md

Start from the role models: borrow how titles are built, overviews open and close, and what the first lines carry; structure, never sentences.

For SEO, Google Ads, WordPress or GoHighLevel, first read the matching file in `templates/profile/` (orientation and vocabulary, never text to paste). Title, hook, skills, portfolio titles and video all follow the recorded direction; if the live profile points elsewhere, write for the recorded direction and say so.

Fix every Step 2 finding in the draft. A finding needing the member's hands becomes a line in `## Profile fields` or `## Completeness` with its cost. Never copy a finding into the file: a checklist in a client-facing overview is a bug.

Write in the member's own voice per `references/profile.md` and `references/copy.md` (plain words, no em-dashes).

First three lines, then a `# Decide first` block with the open items, then the sections:

```
# Your Upwork profile

Written <today's date> · every number backed by your own evidence
**Next:** put the sections live in Step 6.
```

**The picks: one call, before a word is written.** Whatever is the member's promise or taste is theirs to choose, as a pick and never as a text to approve. Put four single choices in one call, three options each, your recommendation first with its reason in the description and the exact text in the preview:

1. **The title**, three of them, each built `Keywords | Hook` as the Title rule below sets out.
2. **The hook**, three opening lines for the overview.
3. **The offer**, three ways to say what a client gets, each as two to four generic stages that fit any job in the branch (part 4 below). The options differ in what comes first and which outcome leads.
4. **The risk reversal**, four options: two promises about delivery they could keep, one result guarantee, and none. The guarantee is offered and never recommended: "If I do not get you [the outcome], you do not pay", its figure typed by the member, with what it costs in the description (unpaid work when it misses, and a refunded Upwork contract leaves no public review). Write the pick into `**Risk reversal you offer:**`.

**Facts are never a menu.** Social proof, results, skills and numbers come from the evidence and the count, strongest first; the member does not choose among them. Take a position inside the picker: if the member objects to your recommendation, answer on the merits once, then write what they picked. Never open with "fair point". A dismissed pick means your recommendation stands and is listed under Decide first. Then write `profile.md` and run the gate.

Then these sections with these exact headings (the gate reads `## Title`, `## Overview`, `## Skills`, `## Portfolio titles`, `## Reference averages`):

- **`## Title`**: the picked title alone in a fenced `text` block, reason in one line. **Two parts, `Keywords | Hook`.** The keyword part is the role with its main search term plus one or two more, the highest-counted names from Step 3 that are also in the skills list; the gate checks exactly that part. The hook is the last block: what the client gets or who it is for, in plain words, no price, no years, no badge words. Keywords come first because a title search matches the title alone and a proposal card cuts the title short. Position the member as a general expert of the branch ("SEO Expert"), not a niche role, unless their background brings it. **Maximum 70 characters**; the gate fails longer.
- **`## Overview`**: the first two lines once alone as a quote, then the whole overview in one fenced `text` block, no markdown. **Five parts in this order (ruling of 10 October 2026: the first two lines are all most clients read, so the promise goes there), each a line or a short block. A part with nothing true to say is left out, never padded:**
  1. **Hook and risk reversal.** The opening, one or two sentences. First about 20 words in "you"/"your": the outcome this client wants, from the recorded direction. It has to land cold on one read: one idea, plain verbs, and no word that points back at an earlier one ("so you see which ad brought each one" loses the reader; "I run Google Ads that turn more of your budget into booked jobs" does not). Then, in the same line, the risk reversal the member picked, word for word as recorded in `**Risk reversal you offer:**`: a promise about delivery they can keep (a small first milestone, a working draft before the first payment is released, fixes until it works within the agreed scope), or the result guarantee they chose with their own figure ("If I do not get you a 2x return, you do not pay"). Never write a guarantee they did not pick or a figure they did not type; the gate lets a guarantee's figure through only inside that recorded sentence. A member who picked none opens on the hook alone.
  2. **Social proof.** Why to trust the member before any project is named: who vouches for them and what they were trusted with. A badge, score or earnings figure, a client's own words, a named brand or employer, the size of what they were responsible for, a certification, a count of clients or years. Take the strongest two or three by tier (`references/profile.md`, Rank the proof) in one line, said in the first person as something the member did or holds ("At my last agency I managed $280,000 a month in ad spend"), never "trusted with" or "an agency trusted me". **It is never a project result:** those belong to part 3, and a result here leaves the profile with two layers of results and no social proof. The opening and the social proof both sit inside the first 250 characters.
  3. **Results.** Up to three Built/Delivered lines (what, for whom, the result with the member's number, the timeframe), highest tier first, **with the client named wherever the member may name them**: "Bright Smile Dental" is believed, "a dental group" is doubted. At most 20 words each: the outcome only, no process, steps or tool lists. The only list in the overview.
  4. **About you and how you work.** A short block: the background that makes the offer believable, a differentiator only if Upwork does not already show it, and the offer. What they get, as two to four stages in order, **generic enough to fit every job in the branch**: clients arrive with many different jobs, and an offer written for one of them turns the rest away. Each stage names a kind of work and what the client gets from it ("I audit your account and fix what is broken, so you know which ads make you money. Then I improve your ads to bring your cost per lead down. Each month you get a report that shows your leads, booked jobs and return."). Never the procedure of one job ("one test form and one test call"), a tool or a duration: those belong in the proposal for that job. The stages aim at an outcome and never promise one: a promise is the risk reversal's job. **On a profile with no reviews at an entry rate, one line says why the rate is low and that it will rise:** new on Upwork (or rebuilding here), charging more once the profile is established. Years of experience beside a starter price is exactly what a client doubts, and said out loud it becomes the reason to hire now.
  5. **Call to action.** One imperative, plus permission back to "you".

  **Write it as copy, not as a description** ([references/persuasion.md](../../references/persuasion.md)). Every line gives a feature, the benefit it brings and what that means for the client; where there is room for one, keep the outcome and drop the feature. Answer a fear the client has (persuasion.md, section 4) instead of praising the member. Second person, the client's own words, exact numbers, sentence case. **Below a grade 7 reading level:** short sentences, short words, one idea each, no word the client would need explained first. **Shorter is better:** aim for 150 words; the gate fails past 220 words or at grade 7 and above. Never restate location or the skills list; a badge, score or earnings figure appears only as S-tier proof and exactly as the aggregate states it. With fewer than three results use those; invent none.
- **`## Skills`**: one `- Skill` line each, all 20 slots filled (keywords live in title and skills, never woven into the overview), the top of Step 3's count in Upwork's exact spelling (HighLevel, not GoHighLevel), most asked for first; mark unconfirmed ones "(check the spelling in Upwork's list)". Under them, one line with the bench: the next ten names, to swap in when Upwork rejects one.
- **`## Portfolio titles`**: one `- New title (was: old title)` line per project. A number goes in a title only when the proof ties it to that project; otherwise keep the title as it is. Never ask the member to link results to projects.
- **`## Reference averages`**: from the role models `- title: N` and `- overview: N` in characters, the three URLs, today's date. The gate fails a title or overview more than 20 % above these; without role models only Upwork's limits apply.
- **`## Video script`**: one connected intro pitch in a fenced `text` block, only the words to read, about 45 seconds (about 100 words) unless the member names another length. **The same five parts as the overview, spoken in this order:** the hook with its risk reversal, the social proof, one or two results, a line about you and how you work, the call to action. Derive it from the overview and the picks, never invented beside them. **This is the video about the person:** the member on camera, introducing themselves, with nothing to screen-share. A result may be put on screen for the seconds it is said, but that is optional; the walkthrough of the work belongs to the proposal video (`/proposal`), never here. No headings or announcing sentences. Client first names only if the member gave them. Warm, plain, contractions, one idea per sentence, numbers as said aloud, no pressure, no big promises. Close with "read it aloud once before recording; anything that trips your tongue gets cut". The member records it and gives a public YouTube link, set in Step 6 (10% of completeness) and written into `**Intro video:**` in `context/me.md`; the profile goes live without it. It is the video about the member. The video about the work, for proposals, is written by `/proposal video`.
- **`## Profile fields`**: the remaining fields, paste-ready, from `context/me.md` only: Employment history (each relevant role with employer, title, period, non-freelance work included; no invented lines about what customers got), Education, Languages with English level, Availability in hours per week, Categories matching the direction, Hourly rate (band and number to enter), Photo (its grade from Step 4b and what to fix), Linked account (which), Other experiences (volunteer work, side project, system built at a non-freelance job). A field still open after Step 4b gets one line: what is missing and its cost.
- **`## Completeness`**: the shortest route to 100 as actual clicks, against the published percentages. State the Step 2 number, or for a new profile the fields to create, cheapest first.
- **`## Paste order`**: click-by-click placement of each section the connector cannot write, and of everything if a write fails.

## Step 4b · What only the member can tell you

`context/me.md` does not hold everything a complete profile needs, and a field printed as "missing" is a field that stays empty. Ask for every one that is open, as picks in one call, and write each answer back into `context/me.md` after saying the line you will add.

1. **Availability.** Single choice: more than 30 hours a week · fewer than 30 · as needed, open to offers. It goes live through `update_availability`; the preview shows Upwork's exact label.
2. **Photo.** Single choice: I have one for you to check · I need to take one. Then the file, by path or dropped into the chat.
3. **Linked accounts.** These are public accounts on other sites that Upwork lets a profile connect, worth 10 points of completeness for one click. Checkboxes: GitHub · Stack Overflow · Behance or Dribbble · none of these. DeviantArt and Twitter count as well and LinkedIn does not (Upwork's community answer of April 2021, so read today's list in the profile editor). The member links it by hand.
4. **Client names.** For each result in the overview whose client is unnamed, one single choice: name them (typed) · keep them as a kind of company. A member names only a client who would not mind, and the name goes into that result's entry in `context/me.md`.
5. **Anything else still open** among English level, other languages, education and categories, each as a pick where the options are known. More than four open questions make a second call.

**Judge the photo before it goes up, out of 10, with a floor of 9.** Open the file and grade the picture, never the person: say nothing about their looks, age or anything else about them. One point each:

1. A real photo of the member: no logo, drawing, stock picture or AI-made image.
2. One person only.
3. Head and shoulders fill the frame, so the face still reads at thumbnail size.
4. The whole face is visible: no sunglasses, hat shadow, mask or hand.
5. Sharp, neither blurred nor pixelated.
6. Even light on the face: no hard shadow, not lit from behind.
7. A plain background with nothing that pulls the eye.
8. Eyes to the camera.
9. A relaxed, friendly expression.
10. Clothes a client of this branch would expect, with nothing distracting.

The first four are Upwork's own photo rules, and a photo that breaks one gets a profile rejected; the rest are reasoned. Give the grade, then each miss with its fix in one line ("stand facing a window", "crop to head and shoulders"). Below 9, ask for another picture and grade that one; the profile does not go live with a photo under the floor. The upload itself is the member's click.

**Fewer than four projects for the portfolio?** Four is where completeness caps out, and an empty portfolio is the first thing a doubting client checks. Recommend the quickest honest way to fill it: take a blueprint from the Blueprints section of the Automatable classroom on Skool (skool.com/automatable), build it for a real business in their branch or as a sample, measure a before and after, and add it titled by its outcome. Upwork allows sample work in a portfolio. It is the member's own build and is described as one, never as a paying client's result. Write what they will build under `**Proof to build:**` in `context/me.md`.

## Step 5 · The gate

Run `python3 code/profile_draft.py check profile.md`: it re-checks Upwork's limits, the `## Reference averages` ceiling, the overview's reading grade (under 7) and length (220 words at most), and every number against the evidence sections of `context/me.md`, video script included. It does not check the portfolio count. With `video` focus add `--only video`. Exit 1: fix and rerun. Never loosen claims or add a number to pass; those sections change only with the member's word or the connector's.

When the gate passes, **always print the video script in full in the chat**, as a quote the member can read aloud, with the recording steps below it (record it, upload as a public YouTube video, send the link). Never only point to the file. Do the same for the title and the overview in the preview message.

## Step 5b · The worst critic, and the floor: chosen over the next nine

The gate counts; this judges. Before anything is previewed, the profile is read the way the member's harshest client would read it: ten profiles open, twenty seconds each, let down before.

**The floor is a choice, not a score.** The question is the one a client really answers: would I pick this person over the next nine? Against Top Rated profiles a beginner loses that every time, and the comparison teaches nothing. So the nine are of the member's own standing: for a profile with no reviews, nine other new profiles in the same branch at a similar rate; for an established one, nine with a similar record. Among its peers this profile has to be the one that gets the message.

**Who judges.** A fresh reader, never the writer. Hand a subagent only what a client sees on Upwork (the title, the overview, the skills, the rate, the portfolio titles, and whether the profile shows reviews, a badge or earnings) with the brief below, and none of your reasoning or the member's file. The newer low-review profiles read in Step 3 go along as they are, unnamed, as the first of the nine ("Profile B", "Profile C"); the critic fills the rest with the typical profile of that standing: a greeting, a list of tools, "hard-working expert", no numbers. Without a subagent tool, reread the fenced text cold and judge it the same way.

**The brief.** "You are a client hiring for <the typical job of this direction>. You have been let down by freelancers before. You have this profile and nine others of the same standing open. Read it once, as it appears on Upwork. A profile cannot link out and most freelancers cannot show a review, so never ask for something to check: this is a trust call, and the question is whether what is written is specific and plausible enough to trust. The title is a search field and carries the terms clients type, so judge it for fit, not for plain words. First answer the ten questions yes or no, quoting the words that decided each; a yes needs evidence in the text and any doubt is a no. Then say how many of the nine you would choose this profile over, which kind of profile beat it and why, and the one reason you would close this tab."

1. In the first two lines, do I see my problem or the outcome I want, and not the freelancer?
2. Is there social proof inside the first 250 characters, specific enough that I take it seriously?
3. Are there at least two results with a number, a client and a timeframe?
4. Do they read as true: specific, plausible, a client named where one can be, and anything that looks too good explained?
5. Do I know what I get, and what happens first?
6. Is my risk covered by something concrete?
7. Does the price make sense for what this profile shows, and does the profile say why?
8. Can I take it all in within twenty seconds: short, plain, no word I would need explained?
9. Apart from the social proof and the lines about them, does every line tell me what it does for me?
10. Is the next step obvious and easy?

**The ten answers are the diagnosis; the choice is the floor.** The profile passes only when the critic would choose it over all nine. Show the member the count as a win, so nobody reads it backwards ("beats 7 of 9 rival profiles, one still wins"), what beat it, every no with the critic's reason, and the one reason to close the tab. Never round up, never judge your own draft, never argue with the critic: fix the profile.

- **A no that writing can fix** (order, length, wording, a missing next step): rewrite, pass the gate again, and have a new fresh reader judge it. Three rounds at most.
- **A no that only the member can fix** (no result with a number, no social proof at all, a client who could be named and is not, nothing to cover the risk): writing cannot pass it, and inventing or inflating to reach the floor is worse than failing it. Name what is missing and the shortest way to get it: `/about-me proof`, an item under `**Proof to build:**`, a client's name, a lower rate.
- **Still not chosen over all nine: the run stops here.** Nothing is previewed and nothing goes live. The verdict is HELD, `profile.md` keeps the draft with the count and the open noes under `# Decide first`, and the next action is the member's.

A focus run that changes the title or the overview is judged too; `video` is not.

**Write the verdict into the file, then build the page.** The last section of `profile.md` is `## Client critic`, in this exact shape, because the page reads it: one line on who judged and when, then `**Chosen over:** N of the next 9`, `**Compared with:**` and who the nine were, `**Verdict:** READY` or `HELD`, `**Would close the tab because:**` and the critic's sentence, then one bullet per question, noes first, as `- **No · the question in a few words.** the critic's reason` or `- **Yes · the question in a few words.**`. Then run `python3 code/profile_page.py --open`: it renders `profile.html` on the same sheet as the resume in `context/overview.html`, from one stylesheet (`code/context_page.py`): name and title on top, what shows in search as the quote, the critic's choice and the gate's counts as the row of figures, the portfolio titles as cards, then the overview, video script, employment and fields with the critic, the gate and the skills beside them, and Decide first in the note underneath. **Everything the member pastes copies with one click:** the long texts have a Copy button and every other field is the button itself, so a field you add to `profile.md` has to reach the page as a copy field. It opens the page. Run it again after every change to `profile.md`, held or not, and link both files in the report.

## Step 6 · Put it live, with one yes, and report

Only a profile the critic chose over all nine in Step 5b reaches this step.

The connector documents `update_profile` previews for title, overview, skills (`set_skills` takes 20 names and resolves each against Upwork's own list: a name it rejects is swapped for the next on the bench and the preview is made again), video (`set_video`, public YouTube link), availability, employment (country as ISO code, role up to 50 characters), education, languages and other experience; the title write was tested on 7 October 2026 (at least 4 characters, overview at least 100, skills at least one), the rest is untested. Before writing over a live title, overview or skills, save them to `profile-before.md` in the repository root (gitignored). Write only when the action returns the documented preview, otherwise hand over the paste-ready text and click path. Hourly rate, portfolio, photo, categories and the linked account stay manual.

Create the previews for every writable field first and show them together in one message, each with its exact before and after. Ask once, in one call with two single choices. The first: put all of these live, choose which, or not now; "choose which" is followed by the fields as checkboxes, ticked meaning it goes live. The second is the rate: your recommended number first, one step lower and one step higher beside it, another number typed. **A rate above your highest option gets told so, once, before it is written:** say plainly that it is too high for this profile and why (no review and no badge yet, what clients pay newcomers in their country, and that clients filter by rate so a profile above their band is never shown), what it costs them (applications that get no reply while the Connects are spent), and the number you would start at. Then one single choice: start at the recommended rate and raise it per review, or keep theirs. Their pick stands and is written as they chose; never argue it twice. Say nothing about preview expiry or what comes next. Call `confirm_preview` only for the fields that pick covers (recreate a preview that expired). A dismissed question, or a vague "ok" to a different one, is not a yes. If behavior differs from the documented preview flow, stop and hand over manually.

## Step 7 · Check what is online, then report

When the member says everything is online, read `get_profile` action `get` and `list_highlights` fresh (never the saved files), run `python3 code/profile_checks.py data/profile.json data/highlights.json --json`, and give the completeness number, then two lists. **Online**: what the read confirms. **Still yours to do**: every missing or unreadable field with its percentage and exact click (photo, categories, rate, portfolio, linked account, the video unless `set_video` ran). List what the connector cannot read under "Still yours to do" instead of asking, never assume it is done.

Then run `python3 code/pipeline.py prune` and give the completion report per CLAUDE.md: what is live, what stays manual, the critic's choice (chosen over N of the next 9) as the one check, completeness number, worst gap first, three lines at most. Link [profile.md](../../profile.md) and [profile.html](../../profile.html). Next: `/find-jobs`. Rerun only when something real changes. End with `Upwork calls: N`, measured, never estimated; every field put live adds two.
