# Upwork: what we found out, and how well it holds

This is knowledge about Upwork, not part of the tool: no command reads it, nothing here is an
instruction, and it can be handed to anyone who wants the research rather than the machine. State of
28 September 2026; the underlying sources were read on 26 September 2026 unless a line says
otherwise.

**Evidence labels.** **[Upwork documented]** stands in an Upwork help article, resource page or
product page, cited by article number under `support.upwork.com/hc/en-us/articles/` or by URL; help
articles carry no date of their own. **[Measured]** comes from a scrape or from our own reading of
the Upwork connector, with sample size and date attached. **[Study]** is peer-reviewed or otherwise
published research, with its population. **[Practitioner]** is a vendor, a coach or a freelancer
reporting their own numbers: useful, unaudited, usually with something to sell.

---

## 1. How am I measured

### The Job Success Score

**[Upwork documented]** The JSS is recalculated daily over three windows, 6, 12 and 24 months, and
**the best of the three counts** (articles 211068358 and 38437458199059).

The published formula is successful contract outcomes minus negative outcomes, divided by total
outcomes. The score appears once there are at least two outcomes in 24 months with at least two
clients (38437546570643). The clock runs from the **last transaction**, not from the end of the
contract (38437480577939).

**What feeds it** (32389629156755):

- Client satisfaction, and **private feedback counts**, which may differ from the public review.
- Long contracts weigh more. Payment beyond 90 days counts as a successful outcome even without
  feedback, and each further 90 days counts as an additional job, up to a weight of eight.
- Higher earnings on a contract weigh more.

**Ineligible outcomes:** older than 24 months; no earnings, or a cancellation before payment with no
feedback; no client feedback at all; a client who broke Upwork's policies.

**What lowers it** (38440123106195, 38439816969875): negative feedback, a cancellation without
payment, disputes, losing long-term clients, poor feedback on a well-paid contract. No payment
**and** no feedback has no effect. No payment **with** negative feedback does.

**The thresholds Upwork names:** above 90% is called excellent; below 79% Upwork says a member "may
find it difficult to connect with new clients" (211068358).

**Removing feedback:** only for a terms violation, within seven business days, one report per piece
of feedback (219801228). The old Top Rated perk that let a member erase one bad review is no longer
documented there.

**Not documented, and nobody outside Upwork knows it:** the exact weighting, and what a given star
rating is worth in the formula.

### The badges, reviewed every two weeks

Upwork gates paid consultations behind a badge and names **Expert-Vetted** there as a fourth badge
beyond the three with published criteria. **[Upwork documented]** Expert-Vetted is invitation-only,
screened by a talent manager, and visible only to Enterprise and Business Plus clients
(17932660179475). Nothing about it has been measured here, so it is named and not described.

**Rising Talent** (360049702614). Either an Upwork invitation, or the published bar: an average of
4.8 stars plus at least $250 earned in twelve months. On top of that, a 100% complete profile, a
proposal or work inside 90 days, a JSS of 90% or better if one exists, no account holds, **no
negative public or private feedback**, a verified identity, a valid payout method, and good
standing. The measurable benefit is **30 Connects**, about $4.50, plus the badge and consultations.
No ranking weight is published and no before-and-after numbers exist.

**Top Rated**, the top 10% (211068468). JSS at 90% or better, a first project more than 90 days ago,
Rising Talent or a JSS of 90% in 13 of the last 16 weeks, a 100% complete profile, at least $1,000
earned in twelve months, current availability, good standing, and activity inside 90 days.

**Top Rated Plus**, the top 3% (360050417233). Top Rated held, more than $10,000 earned in twelve
months, and at least one large contract in twelve months with earnings in it and no negative
outcome. "Large" depends on the category: **$5,000** in design, engineering and architecture, legal,
translation and writing; **$15,000** in web, mobile and software; **$20,000** in customer support;
**$10,000** everywhere else.

**How a badge is lost** (360052511133). Taking payment off the platform, or repeatedly moving
communication off it before a contract exists. The badge goes and cannot be earned again for **six
months**.

---

## 2. What can I measure myself

### The numbers Upwork shows, and where

**[Upwork documented]** Behind the profile picture, **Stats and trends** at `upwork.com/nx/my-stats`
(article 211062968):

- **Earnings** over twelve months.
- **Job Success Score** with its insights.
- **Profile metrics:** profile views, invitations, and impressions with clicks **only while a boost
  is running**, plus whether the availability badge was on.
- **Proposals:** sent, viewed, interviews, hires, split into boosted and organic.
- **Connects** balance and spend, the badge, and the eligible weeks inside the 16-week window that
  Top Rated counts.

Figures update roughly every 24 hours. **Freelancer Plus adds Proposal Insights** for hourly,
organic proposals only: how many freelancers applied, how many proposals were opened, shortlisted or
answered, the average bids, and the top skills of the competition (article 34019683309587).

### What does not exist

**[Upwork documented] Upwork refuses to explain its ranking.** Asked how profiles are ranked, Upwork
answers that revealing it "could make it easier for some users to artificially boost their rankings".
It names only platform-generated data such as completed projects and client feedback, plus the
freelancer's own service descriptions. **The old article on how profiles are ranked returns 404**, so
the refusal is now the whole documented answer.

**[Upwork documented, absence checked on article 211062968] There is no search-appearances number.**
Impressions exist only inside a paid boost, so a member cannot see whether a profile change moved
them in the search results at all. Anyone selling a service that promises to show search appearances
is inferring, not reading.

**Profile views cannot be attributed.** A view happens because a client opened a proposal, saw a
boost, or found the profile in search, and the number does not say which. A rise in views after a
rewrite is evidence of nothing on its own.

**There is no documented change loop.** Upwork publishes no method for testing a profile change, and
no practitioner source with checkable numbers survived our filter. **Before and after cases: none
documented, none found.**

The platform still fixes the shape of any honest test:

- Figures lag about 24 hours and eligible weeks tick weekly, so a window shorter than **two to three
  weeks** measures noise.
- One variable at a time: title, or opening, or rate, or targeting. Two at once and the result is
  unreadable.
- Count the four things the member controls and that the stats page carries: applications sent,
  proposals viewed, replies that were real conversations, and hires. They are not confounded by
  boosts as long as the boosted and organic split stays separated.

### Certificates, and what they are really worth

**[Upwork documented]** Upwork's own **Skill Certifications are discontinued**; the ones already
earned stay visible (article 360052720974).

**[Upwork documented] Testimonials are closed.** Upwork no longer accepts new testimonial requests
(article 1500002004322), so a member outside the platform cannot collect one to fill a thin profile.

**Partner Certified Talent is the one with a hard number.** Upwork partners with MindStudio, Podium
Education and Webflow, calls the certifications "often free or discounted", grants **150 free
Connects per new partner certification**, adds a Partner Certified badge, and states the
certification is "factored into Upwork's search and matching". Page dated 22 September 2026,
`upwork.com/partner-certification`. Two certifications are 300 Connects, worth about **$45**, which
is the only documented return in this entire area.

**[Practitioner] Outside Upwork, per lane:**

- **Make Academy is free**, with Credly badges.
- **n8n course certificates are free**; its real certification exam is still announced as coming.
- **GoHighLevel Certified Admin costs $970 a year**, and the badge switches off when the
  subscription ends, which makes it a poor first purchase.
- **No official WordPress certificate exists.**
- HubSpot Academy is free. Meta's associate exam is $99. Salesforce learning is free with paid exams
  from $200.

**[Measured] Do clients ask for any of this?** On 26 September 2026 across the 40 newest postings in
our four lanes, ten each: **exactly one posting mentioned a certificate at all**, as "a plus", and
it was a HighLevel certification. **Zero mentions** of Make, n8n, HubSpot or WordPress certificates.
Clients ask for a walkthrough, examples and sometimes a paid test task.

---

## 3. How do I start from zero

For a member with no reviews, no Job Success Score and no Upwork history.

### What Upwork itself says about being new

**[Upwork documented]** Proposals are sorted by the profile, the Job Success Score and how well the
cover letter matches the posting, and a client sees the photo, title, rate and JSS before opening
anything (`upwork.com/resources/why-are-my-proposals-not-being-viewed`). Without a JSS the member
starts structurally behind, by Upwork's own account. The four things visible before the click are
therefore the four that must be right: photo, title, rate, and the badge line that is empty at the
start.

### The hard number about which work is open to a beginner

**[Measured]** Under **9% of projects posted in 2025** were open to freelancers with no history,
down from roughly **15% in 2024**. By category: IT around **4%**, while admin, translation and
customer service sit near **20%** (Vollna, 2.2 million projects scraped, about 95% coverage,
`vollna.com/reports/upwork-projects-trends-2025`). A vendor's scrape, not Upwork's data, and the
page carries no date.

### Where a career background helps, and where it does not

**[Study]** A peer-reviewed study of 60 freelancers found that "workers' non-platform experience
contributes little to their platform-specific reputations": titles, employers and degrees earn
almost nothing inside Upwork's reputation system, and the badges require platform activity
(Administrative Science Quarterly, 2026, reported September 2026,
`phys.org/news/2026-09-online-platforms-misaligned-late-career.html`).

This is the sharpest counter-argument to using a career changer's history at all, and it is right
about what it measures. The distinction that survives it: prior experience buys **no reputation**,
and a client still reads the overview with their own eyes. Background belongs in the copy, where a
human decides, never in a claim about standing on the platform.

### Speed, measured on somebody else's account: the GigRadar proposal study

**[Practitioner]** Across **133,872 proposals from 322 agency teams between December 2025 and
February 2026** (`gigradar.io/blog/upwork-outreach`):

- Applying **3 to 4 minutes** after a posting produced an **11.86% reply rate**, against **5.34% at
  30 to 45 minutes**, and **6.91% from minute five onward**.
- The **average reply rate was 7.45%**.
- The **top quartile of teams reached 12.86%**, the bottom **3.76%**.
- Opening the cover letter with a **question rather than a pitch** correlated with a **479% higher
  reply rate**.
- **Boosting with 21 to 30 Connects performed worse than not boosting.**
- Their **cost per hire works out near $60**.

The caveats are as important as the numbers: automated agency accounts, a vendor with a product to
sell, and no beginner in the sample. It is still the largest set of published numbers on proposal
timing, and it points the same way as everything else: the window after a posting is short.

### Connects, boost and the numbers that move

**[Upwork documented]** A Connect costs **$0.15**, bought in bundles of ten. Upwork states no range
of Connects per job, only that it varies with project size and demand.

**Boost is an auction** for four top slots, billed only when the bid lands in the top four at close
or when the client engages. The auction **closes after seven days or at the first hire**. A
displaced proposal's boost is **refunded when it drew no client interaction**, while the base
Connects are charged either way.

**[Practitioner]** The "placebo auction" story that circulates in communities appears in no Upwork
source; treat it as rumour. Upwork's own claimed boost effect has moved from 37 and 43% in beta, to
55% in 2023, to "up to 24%", always relative and never against a stated baseline, which on a reply
rate near 4% is small either way. **The 24% belongs to boosted proposals, not boosted profiles**: for
a boosted profile Upwork promises only "may help you gain increased visibility" and publishes no
number at all.

**[Upwork documented] The availability badge is sold on a number that does not hold still.** The page
claims "up to 70%" more job invites while indexed snippets of the same page still say 50%, which
makes it marketing rather than measurement, and Upwork states in its own FAQ that the badge does
**not** change search position
(`support.upwork.com/hc/en-us/articles/40368040805907`).

**[Practitioner] The counter-case.** One freelancer reports **$600,000 earned without buying a
single Connect or boost** (Morgan Overholt,
`morganoverholt.com/editorials/get-first-job-on-upwork/`). She also documents her own start: **13
applications in under two weeks, a first job worth $10, and $6,000 a month after three months**, by
delivering the work before the client agreed to hire.

**[Practitioner] The one paid-feature test anybody published.** The same freelancer ran **30
proposals in April 2024** and reported the split (`morganoverholt.com/upwork/upwork-paid-features/`):

- Her baseline was **50% of proposals viewed, 20% replies, 10% hires**.
- The week she carried the **availability badge, views dropped to 20%**.
- **Boosted proposals reached 80% views**, at **$32.70 in Connects across ten applications**.
- A **boosted profile changed almost nothing and drew zero invitations**.

One person, 30 data points, two years old. It is indicative and not transferable, and it is still the
only before-and-after on Upwork's paid features with numbers attached.

**Application volume against profile quality has no beginner data at all.** Nobody should imply that
it does.

### The three most repeated claims with the weakest support

1. **"Pick a niche and earn two to four times more."** The circulating figures contradict each
   other, cite "Upwork data" with no source, and describe the hourly rates of established
   freelancers rather than a first contract.
2. **"An intro video gets you 30% more views."** The number traces back to a page that cannot be
   opened, and nothing else supports it. This is why an intro video is optional.
3. **"Rising Talent and specialized profiles for visibility."** Specialized profiles no longer
   exist, and Upwork states the removal did not change rankings.

---

## 4. What does the market pay

### Upwork's own published ranges

**[Upwork documented]** From `upwork.com/resources/upwork-hourly-rates`, published **18 June 2025**
although the page is titled for 2026, with no update marker, so the real age is unknown. These are
**asking rates from profiles, not rates anybody was paid**:

- Marketing automation consultants $40 to $90
- Chatbot developers $30 to $61
- CRM consultants $16 to $35, HubSpot $15 to $40, Salesforce $25 to $40
- Web developers $15 to $50, web designers $15 to $30, WordPress $15 to $28, Webflow $20 to $45
- SEO experts $15 to $35, SEO analysts $25 to $50
- AI developers $30 to $50, AI engineers $35 to $60, machine learning $50 to $200

**Upwork publishes no rate page for Make, n8n, Zapier or GoHighLevel.**

### Measured from real postings

**[Measured]** A third-party scrape with its method disclosed: **11,541 postings over the 30 days to
16 May 2026** (Upwatcher).

- Keyword "ai automation", **707 hourly postings**: median **$30**, lower quartile $20, upper
  quartile $40, ninth decile $60.
- Platform-wide across **4,542 hourly postings that stated a rate**: lower quartile **$18**, median
  **$25**, upper quartile **$38**, ninth decile **$55**.
- By the experience level the client picked: entry level **216 postings, median $18**, lower
  quartile $12. Intermediate **2,708 postings, median $25**. Expert **1,617 postings, median $36**,
  upper quartile $48, ninth decile $70.
- **Intermediate is 62% of all postings; entry level is only 4.4%.**

**Fixed price against hourly, same source:** **61% of postings are hourly, 39% fixed**, and the
median fixed budget is **$150**. The distribution is bottom-heavy: **1,728 postings under $100,
1,337 from $100 to $500, 474 to $1,000, 767 to $5,000, 139 to $10,000, 89 to $50,000, and 17 above
$50,000.**

### Measured through the Upwork connector, 26 September 2026

**[Measured]** Eleven searches, the ten newest postings per lane, sorted by recency. A snapshot of
one day, not a distribution.

**Fixed price, where every posting stated a budget.** GoHighLevel median **$625** ($5 to $2,000).
n8n median **$160** ($10 to $3,500). Chatbots median **$75** ($20 to $4,750). WordPress median
**$57.50** ($10 to $550). Typical proposal counts 18 to 41.

**Hourly, where the postings go quiet.** n8n stated a rate in 5 of 10, chatbots in 4 of 10,
WordPress in 8 of 10, GoHighLevel in 8 of 10. Where a range exists, the medians run **n8n $15 to
$25**, **chatbots $25 to $42.50**, **WordPress $10 to $25**, **GoHighLevel $8 to $25**, with a
single posting at $40 to $90.

**The entry-level filter is the finding that matters.** Filtering GoHighLevel to entry level returns
rates with a median of **$4 at the bottom and $10 at the top**, and **5 of those 10 postings run
longer than six months**: long-term work at $4 to $12 an hour. WordPress entry level looks the same,
4 of 10 long-term at a $12 median. Chatbots and n8n barely fill a page of entry-level work at all, 7
and 4 hits before the results ran out.

The beginner lane is not a cheaper version of the same market, it is a different market, and a
member who enters it at $5 anchors themselves there for six months.

**Caveats from the same run.** The `expert` label says nothing about the budget: a $5 fixed-price
GoHighLevel posting and a $10 WordPress one both asked for experts. Proposal counts reach **169** on
a single $15 to $25 n8n job. Half the chatbot hourly results were voice recording gigs from one
client rather than development work, which pulls that median around. And `total_spent` is missing
for most clients in two of the lanes, so a client's history often cannot be judged from a search row
at all.

### The August 2026 automation market

**[Measured]** A monthly scrape published through Maker School, August 2026: **2,391 unique
postings** mentioning Zapier, n8n, Make or Power Automate, and 3,636 in a broader automation set.
Jobs were pulled with Apify and classified by keyword, so one posting can count under several tools
and the counts overlap.

Rates there are **posted hourly maxima, not agreed rates**. Across **928 postings that stated one**:

- Median **$32.50**, mean **$36.91**, quartiles **$18.25 and $50**.
- **35.2% of postings were below $25**, up from 30.9% in July.
- Only **78 postings, 3.26%, asked above $75**; **nine above $150**; the highest was **$250**.
- Fixed price was **37.1%** of postings, down from 42.9% in May.

**Tool mentions, as shares of the 2,391:** **Zapier 1,070 (43.66%)**, **n8n 960 (39.17%)** and
rising every month since May, **Make 421 (17.18%)** and falling from 24.68% in May, **Power Automate
29**. **GoHighLevel appears in 600 postings (25.09%)** and generic CRM in **1,037 (43.37%)**.

The publisher's own caveats matter as much as the numbers: **two scrape days failed and were
backfilled short**, so the monthly total cannot be divided against July's to claim a decline, and
the publisher's two presentations **disagree on the August per-weekday figure, 88 against 92**. Read
it as a list of buyer problems and tools worth investigating, not as a forecast.

### Country: the circular table, taken apart

**[Absence, checked] Upwork publishes no rates by the freelancer's country, and the chain everyone
quotes is circular.** The table naming **$95 for North America, $85 for western Europe, $45 for
eastern Europe, $40 for the Middle East and Africa, $35 for Latin America and $25 for southern
Asia** appears in Clockify citing Jobbers, in GigRadar citing Clockify, and in Upwatcher citing
Jobbers, while the Jobbers page sits behind Cloudflare with no archived copy. The method is
unverifiable. Individual figures for Cameroon or other African countries: nothing at all.

**[Practitioner]** The one survey with a described method, Payoneer's freelancer insights across
more than 2,000 freelancers in 122 countries, reports a **global average of $21 to $22 an hour**,
read through snippets rather than the original.

**[Study]** What is peer-reviewed instead, and more useful: a fixed-effects logit over roughly
**10,000 completed projects on Freelancer.com** found that **the asking rate is not a significant
predictor of winning the job**, while the client's rating of the freelancer and a **match between
client and freelancer country** are significant, and high cumulative prior earnings actually lower
the chance of being hired (Economies 11(3):80, data from September 2018). Another platform, eight
years old, one study.

The honest country advice is therefore not "charge less where you live". It is: apply where your
country and timezone match the client's, because that is the part with evidence behind it, and price
against the discipline and experience band.

### Does a low rate cost you work

**[Upwork documented, unsupported]** Upwork claims a rate far below market makes clients assume
lower quality, and publishes nothing behind that claim. **[Study]** The study above found no
significant effect of the asking rate in either direction. **There is no evidence that a low rate
wins work, and none that it loses it.**

### What an application costs

**[Upwork documented]** A Connect costs **$0.15**, sold in bundles, and Upwork states no range per
job, only that it varies with project size and demand.

**[Practitioner, unverified]** Blogs claim 2 to 6 Connects for a standard job. GigRadar, reading
community reports, claims **14 to 25**, which would be $2.10 to $3.75, and more than 50 for a boost.
Both unverified; the real per-job cost is readable in the posting itself.

**[Absence] How many people apply per job has no reliable number.** One scrape reports 86% of
postings under five proposals and calls that a scrape artifact itself. The one measured figure,
**9.41 bids per project**, is Freelancer.com in 2018.

---

## 5. Which sources did not hold

- **On rates and the market:** of roughly **55 sources examined, 14 survived**. The rest was tool
  and agency content passing unsourced numbers between each other, salary aggregators with no Upwork
  data at all, and community posts about price pressure with no figures.
- **On starting from zero:** of about **40 sources checked, roughly 10 survived**. The rest was SEO
  content from Upwork tool vendors passing the same unsourced numbers to each other.
- **On measuring a profile change:** **no practitioner source with checkable numbers survived at
  all**, and no before-and-after case was found. That absence is the honest state of the art, not a
  gap in the search.
- **The country rate table** is the clearest single failure: three vendors citing each other in a
  circle that ends at a page nobody can open.
- **The Jobbers page** behind Cloudflare, with no archived copy, is the dead end of that circle.
- **The "30% more views from an intro video" page** cannot be opened either, and nothing else
  supports the number.
- **The "placebo auction"** for Boost appears in no Upwork source.
- **Specialized profiles for visibility** was overtaken by the platform. **[Upwork documented]**
  Specialized profiles were **removed on 28 May 2026**, their titles, overviews and skills deleted
  for good, and Upwork states the rankings did not change (article 115013750068). One profile, one
  direction. Blogs calling the removal a new "profile dilution" gatekeeper contradict Upwork, and
  neither side measured anything.

## The three profile samples, and what each is allowed to say

**[Measured]** Everything this system knows about how a working profile is written comes from three
samples read through the Upwork connector. **They must never be merged.** "3 of 3 top earners" and
"12 of 16 arbitrary profiles" are different claims, and a finding that does not name its sample means
nothing.

- **3 top earners**, pulled **14 August 2026**: three high-earning profiles, **$295,000 to
  $1,090,000 earned**, two of them Top Rated Plus, plus one practitioner's bio formula. Practitioner
  evidence rather than Upwork documentation, and three profiles do not prove the pattern caused the
  earnings.
- **16 cross-section**, read **26 September 2026**: sixteen public profiles, **four per lane**
  (GoHighLevel and CRM, Make and n8n, AI chatbots and agents, WordPress). Badges from none to Top
  Rated Plus, earnings **$80 to $200,000**, rates **$6 to $50**. A candidate sample, not a ranking:
  without a client account there is no way to filter by earnings or Job Success. No text was copied,
  because a member who copies a sentence competes with everyone else who copied it.
- **10 postings**, **26 September 2026**: the ten newest GoHighLevel postings, counted for their
  `skills` arrays.

### What those overviews actually do with the reader

**[Measured, 16 cross-section]** The perspective rule every guide repeats, hook in "you", middle in
"I", close back in "you", is not what the text does. Measured as a share of the overview, roughly
**15% is the reader's problem, 70% the freelancer's own abilities, and 10% the reader again**, and
**only two of the sixteen hold the reader's side throughout**. The advice describes the exception
rather than the sample.

### The exception that argues against the house style

**[Measured, 16 cross-section]** The two highest earners in that sample, at **$100,000 and $200,000
plus**, write real prose: **25 to 40 words per sentence and almost no emoji**. The checkmark lists
correlate with the lower earnings instead. Sixteen profiles cannot show which way the causation runs,
and the list is still what a beginner reaches for first.

## Four numbers that lived nowhere else

These were recorded once in a structured fact file that no command ever read.
That file is gone, so they sit here rather than nowhere. All four come from the
Maker School evidence snapshot of 26 September 2026.

- **Freelancer Plus gives 100 Connects a month from the second month.** The price
  is only visible inside the account, so do not budget the old twenty dollars.
  [Upwork documented, sources R10 and M05]
- **A profile needs 50 percent completeness before it can be boosted.** Boosting
  a half-finished profile is not an option Upwork offers. [Upwork documented]
- **The green dot is not the Availability Badge.** Being online for messages is a
  separate, free setting; the badge is paid and filterable. Members conflate
  them. [Upwork documented]
- **The monthly posting scrape is published** at
  `upwork.redwaterrev.com/report/2026-08`. Every rate distribution in the section
  above that names August 2026 comes from that page. [Measured, third party]

## One connector observation that contradicts a popular claim

A masterclass source claims that clients with no spending history pay better,
on the theory that they do not yet know the going rate. One day of connector
data, 26 September 2026, points the other way. The cheapest GoHighLevel
postings came from clients with no spending history at all, while the single
posting offering $40 to $90 came from a client with about $20,000 of history.
Ten postings on one day is no more proof than the claim it argues with, and
both sides stay unmeasured. [Measured, tiny sample]

## What Upwork says about automation

Measured 14 August 2026 from Upwork's own pages, links checked 12 September 2026.
The operating rules this produced live in `references/upwork.md` as constraints
without this reasoning behind them. The reasoning is here.

**Unattended automation is prohibited.** Upwork names two things verbatim as
grounds for enforcement: "Using OAuth2 tokens or session cookies from a browser
or an official client in a script or bot", and "Exceeding rate limits or running
background polling that resembles scraping".
[Source](https://support.upwork.com/hc/en-us/articles/43342677368467-Use-bots-and-other-automation-properly)
Two approaches that would technically work are therefore out: copying a Claude
Code login into another runner, and polling on a schedule. [Upwork documented]

**The published limits contradict each other.** Ten requests per second per IP,
then HTTP 429
([support](https://support.upwork.com/hc/en-us/articles/115015933428-What-are-the-API-requests-limits)),
against 300 per minute
([developer docs](https://www.upwork.com/developer/documentation/graphql/api/docs/index.html)),
which is a factor of two apart. 40,000 per day, confirmed in the API-key
application. Responses may be cached 24 hours at most. Both smaller numbers are
Upwork's own, so assume the stricter. [Upwork documented]

**The pattern matters as much as the volume.** "Polling that resembles scraping"
is a behavioural judgement with no documented threshold. No request count makes
unattended polling acceptable, which is why a human starting every run is the
rule rather than a call budget. [Upwork documented]

**Contact details before a contract can cost the account.** Sharing them, or
asking for them, "before a contract starts is against our Terms of Service, and
may result in temporary restrictions, loss of talent badges, or permanent loss of
account access". A link to your own work is allowed if you ask the client to keep
contact on Upwork, so a linked page may carry no way to reach you.
[Source](https://support.upwork.com/hc/en-us/articles/360051749534-How-to-keep-your-contact-information-safe-on-Upwork)
Exception: on an Enterprise plan, either side may share contact details earlier.
[Upwork documented]

**One contradiction nobody here can resolve.** The connector's own tool
description exposes a `set_tool_permission` switch with an `always_allow` value
and calls it useful for automated flows. That is a technical permission setting,
not policy approval for unattended use. Two Upwork sources, two directions.
Anyone intending to run something unattended has to ask Upwork support and write
the answer down. [Upwork documented, unresolved]

**An open question about this system itself.** Upwork's connector guidance asks a
member to check with support before scheduled activity, AI filtering or scoring of
results, storing connector output, hosted clients, or chaining several tools into
one flow. Two of those describe what the Blueprint does: `/find-jobs` scores
postings with a model, and `pipeline.py` prunes cached job fields in `data/jobs.json`
after 24 hours. Chats live in `jobs/<id>/thread.json`, retained for 90 days by default
so follow-ups and feedback can learn from them. `KEEP_CHAT_HOURS=24` selects the
published 24-hour window; `0` retains no chats. Quotes and inline comments are accepted;
an invalid explicit value warns and uses 24 hours. The longer default is this system's
choice, not Upwork approval. A human starts every run and nothing is scheduled, which was the part
to be careful about. The rest is unanswered. Recorded 26 September 2026, Maker
School evidence snapshot, source R21. [Upwork documented, unanswered]


## Connector response shapes, moved out of references/upwork.md on 28.09.2026

A member reads that file before their second command, so the measurements that only a
maintainer needs live here instead. Nothing reads this file.

- **MEASURED 12 September 2026, `get_profile` action `get` with a `profile_key`** (starts with `~`, from any public profile URL): another freelancer's public profile. The fields sit under `data.talentProfileByProfileKey`, not `data`, and `profileAggregates` adds the badge (`top_rated`), the earnings bucket ("$100K+") and `totalFeedback`.
- **MEASURED 12 September 2026:** `get_freelancer_dashboard` and `list_contracts` action `search` carry no Job Success Score either. The dashboard does show Connects spending line by line; that is how a recurring "Paid invitation badge" charge of one Connect every twelve hours became visible.
- **MEASURED 12 September 2026: the `status` filter on `list_freelancer_proposals` action `list` does not filter.** `Accepted`, `Offered`, `Pending` and `Activated` came back empty with "no submitted proposals yet"; `Hired`, `Declined` and `Withdrawn` each returned the same mixed list, totals 44 to 56. Read each proposal's own `status` field, never trust the filter, and treat an empty list as proof of nothing.

## Compliance sources, 8 October 2026

What `references/upwork-compliance.md` was written from: 84 sources, found and read on
8 October 2026. Only 12 were read in full. `www.upwork.com` and `support.upwork.com`
answer an automated reader with HTTP 403, and that block was respected: those pages were
read as search summaries, so their rules are Upwork's and their wording is unconfirmed.

**Upwork legal text, read in full** from `upwork.pactsafe.io/versions/<id>.pdf`, Upwork's
own contract host (8):

- User Agreement, `68c1a74d9ce539a22de9e26c`. Sections 1.3, 1.4, 1.7 and 7 quoted.
- Terms of Use, modified version effective 10 September 2025, `68b260a5baab1fb4e49a1abb`.
  Section 3 quoted.
- API Terms of Use, dated 14 December 2016, `5ab3ea9c4711726a1e8ac7d7`. It predates the
  combined "API & MCP Terms of Use" now in the Legal Center, which could not be opened.
- Freelancer Membership Agreement, `66441a282e25e21eba83e6ba`.
- Fee and ACH Authorization Agreement, `62696ef23a416e643ed74006`. An older version: it still
  shows 20%, 10% and 5% tiers, where Upwork's 2026 fee page describes 0% to 15%.
- Fixed-Price Escrow Instructions, `6920e0b95a2c6fd4b76c22c2`.
- Client Initiated Direct Contracts Terms, `6887c93cf80cbf71a9f9cd3e`.
- Privacy Policy, effective 5 January 2026, `6933a0e2470973ec9e3cfb86`.

**Upwork help articles, search summary only**, by number under
`support.upwork.com/hc/en-us/articles/` (57):

- Automation, API and AI: 43342677368467, 115015933428, 115015933508, 55446516654611,
  17652357074451, 23808634769683, 22983791592595.
- Contact and circumvention: 360051749534, 360052511133, 360048105134, 17995710125715,
  360043210654, 40444093133331, 17995658941843, 360051750574, 10479573964819, 1500005480882,
  360025040794, 360049702614, 4408071013523.
- Account, profile, proposals, Connects and feedback: 39505058710163, 18513114070419,
  360035562673, 45166686792211, 34397755511955, 360053305673, 211062898, 20850487528723,
  7180643124243, 219801228, 1500007578942, 115003975967, 211062998, 18527060418579.
- Payments, contracts, conduct and data: 211068288, 211063748, 211063718, 44564821903763,
  211062088, 40525891840787, 26106318334611, 227022468, 211060578, 34262531838099, 211068428,
  6474413966483, 211063608, 25205969832083, 1500007569061, 360047360093, 211067778,
  14709449807891, 211063948, 211067798, 46026132679571, 33768351094419, 39081284750355.

**Other Upwork pages, search summary only** (12): the developer documentation
(`upwork.com/developer/documentation/graphql/api/docs/index.html`), `upwork.com/ai/mcp`, the
Legal Center (`upwork.com/legal`, for the API & MCP Terms of Use), `upwork.com/uma`, the
investor release of 10 August 2026 on AI agents, the Hourly Escrow Instructions
(`663130706c4e3b11b539a970`), and six resource pages under `upwork.com/resources/`:
`leading-voices/getting-banned-on-upwork`, `upwork-scams`, `write-proposals-freelancer-advice`,
`4-ways-create-successful-freelancer-portfolio`, `upwork-dispute-process`, `is-upwork-free`.

**Upwork community threads, search summary only** (3), under
`community.upwork.com/t5/Freelancers/`: 1154833 on a Loom in a proposal, 1513419 on a portfolio
site that carries contact details, 1471579 on generative AI.

**[Practitioner], read in full** (4), all vendors with a product to sell and none of it acted
on: `gigradar.io/blog/upwork-account-suspended` (17 May 2026),
`gigradar.io/blog/upwork-automation`, `getmany.com/blog/upwork-ai-policy`,
`giguphq.com/blog/upwork-ai-proposals-banned-2026`. The figure they share, a 23% rise in
automation suspensions in 2025, traces to an Upwork community announcement nobody could find.

**What did not hold or could not be found.** No rate limit is published for the connector. No
page confirmed the connector guidance on scoring and storing output recorded above on 26
September. No Upwork page states a cap on proposals, a follow-up cadence, a rule on a
freelancer keeping chat logs, or the subcontracting rule one summary reported. The conversion
fee reads two ways inside the same section, 13.5% of twelve months and "a minimum of $1,000 USD
and up to $50,000 USD"; both are in the text.
