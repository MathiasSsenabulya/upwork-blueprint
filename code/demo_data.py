#!/usr/bin/env python3
"""A sample pipeline for showing the dashboard. Never the member's own.

    python3 code/demo_data.py [folder]     writes jobs.json and sync.json there (default data/demo)

`python3 code/cockpit.py --demo` calls this and points the dashboard at the result, so
the real pipeline in data/jobs.json is neither read nor written while a demo runs.
Every lead here is invented: no client, job or number in it is real, and the page
carries a "Demo data" badge for exactly that reason. The dates are laid out backward
from today, so the charts always end on the current week.
"""
import datetime
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
UTC = datetime.timezone.utc
# Applications sent per week, oldest first, ending on last week. This week is added from
# the days that have passed. A member who builds up to ten a day looks like this.
WEEKS = (18, 24, 31, 38, 44, 47, 52, 50, 55, 53, 56)
PER_DAY_NOW = 9
JOBS = (
    ('A dental practice wants missed calls texted back within a minute.', 'Missed-call text-back for a dental practice',
     ['Text every missed caller within a minute', 'Log each lead in the CRM', 'Alert the front desk'], 'Has built missed-call flows before'),
    ('A roofing company wants new leads followed up automatically in n8n.', 'n8n lead follow-up for a roofing company',
     ['Follow up every web lead in n8n', 'Book estimates into the calendar', 'Report booked jobs weekly'], 'n8n and a CRM, shown in past work'),
    ('A law firm wants intake forms routed into its CRM.', 'Intake automation for a law firm',
     ['Route intake forms into the CRM', 'Assign each matter to a lawyer', 'Send the client a confirmation'], 'Experience with client intake'),
    ('An HVAC company wants its Google Ads rebuilt to bring in calls.', 'Google Ads rebuild for an HVAC company',
     ['Rebuild the Search campaigns', 'Track calls as conversions', 'Cut the wasted search terms'], 'Local service Google Ads results'),
    ('A med spa wants review requests sent after every visit.', 'Review request automation for a med spa',
     ['Ask for a review after each visit', 'Send unhappy replies to the owner', 'Show new reviews in one sheet'], 'A review flow you can show'),
    ('An online store wants abandoned carts won back by email and text.', 'Abandoned cart recovery for an online store',
     ['Email and text abandoned carts', 'Stop the sequence on purchase', 'Report recovered revenue'], 'Shopify and Klaviyo experience'),
    ('A coaching business wants call bookings confirmed and reminded.', 'Booking reminders for a coaching business',
     ['Confirm every booked call', 'Remind by text the day before', 'Rebook no-shows'], 'Calendar and SMS tools'),
    ('A property manager wants maintenance requests sorted with AI.', 'AI triage for maintenance requests',
     ['Sort requests by urgency', 'Send each one to the right trade', 'Update the tenant'], 'An AI workflow already in use'),
    ('A marketing agency wants client reports built automatically each week.', 'Automated weekly client reports',
     ['Pull ad and analytics data', 'Build one report per client', 'Email it every Monday'], 'Looker Studio or similar'),
    ('A plumbing company wants Local Services Ads set up and tracked.', 'Local Services Ads set-up for a plumber',
     ['Set up Local Services Ads', 'Track booked jobs', 'Dispute the bad leads'], 'Local Services Ads experience'),
    ('A software startup wants trial sign-ups scored and sent to sales.', 'Trial lead scoring for a software startup',
     ['Score every trial sign-up', 'Send hot ones to sales', 'Nudge the quiet ones'], 'HubSpot workflows'),
    ('A physiotherapy clinic wants no-show reminders sent by text.', 'No-show reminders for a physio clinic',
     ['Text a reminder before each visit', 'Offer an easy rebook link', 'Count the no-shows saved'], 'Booking system integrations'),
    ('A recruiter wants candidate follow-ups automated in Make.', 'Candidate follow-up in Make',
     ['Follow up candidates after interviews', 'Update the tracking sheet', 'Flag the stalled ones'], 'Make scenarios you can show'),
    ('A landscaping company wants quote requests answered in five minutes.', 'Five-minute quote replies for a landscaper',
     ['Reply to every quote request fast', 'Ask the three sizing questions', 'Book the site visit'], 'Speed-to-lead automations'),
    ('An accountant wants client documents chased automatically.', 'Document chasing for an accounting firm',
     ['Request missing documents', 'Remind until they arrive', 'File them in the right folder'], 'Client portal experience'),
    ('A gym wants cancelled members won back with a short sequence.', 'Win-back sequence for a gym',
     ['Message members who cancel', 'Offer a way back', 'Report who returned'], 'Email and SMS sequences'),
)
CLIENTS = (('United States', 4.93, 17, 23950, 31, 43), ('Canada', 5.0, 33, 63770, 40, 48), ('United Kingdom', 4.7, 9, 8400, 11, 15),
           ('Australia', 4.85, 22, 20780, 25, 33), ('United States', None, None, None, 0, 1), ('Germany', 4.6, 6, 3100, 6, 9),
           ('United States', 4.98, 51, 112300, 64, 80), ('Canada', 4.4, 4, 1250, 4, 7))
BUDGETS = (('hourly', '25.00–45.00/hr'), ('fixed', '$400'), ('hourly', '30.00–60.00/hr'), ('fixed', '$750'),
           ('hourly', '20.00–35.00/hr'), ('fixed', '$1,500'), ('fixed', '$250'), ('hourly', '40.00–75.00/hr'))


def stamp(moment):
    return moment.astimezone(UTC).isoformat()


def lead(n, rng):
    headline, title, scope, must = JOBS[n % len(JOBS)]
    country, rating, reviews, spent, hires, posted = CLIENTS[rng.randrange(len(CLIENTS))]
    job_type, budget = BUDGETS[rng.randrange(len(BUDGETS))]
    checks = {name: rng.random() < odds for name, odds in (('main_offer', 0.55), ('tools', 0.7), ('proof', 0.5))}
    fit = 7 + sum(checks.values())
    return {
        'id': str(9_000_000_000_000 + n), 'title': title, 'headline': headline, 'summary': headline, 'url': None,
        'budget': budget, 'job_type': job_type, 'engagement': 'PART_TIME' if job_type == 'hourly' else None,
        'skills': [], 'found_via': ['demo'], 'proposals': rng.choice(('Less than 5', 'Less than 5', '5 to 10', '10 to 15', '20 to 50')),
        'client': {'country': country, 'rating': rating, 'reviews': reviews, 'spent': spent, 'hires': hires,
                   'posted_jobs': posted, 'verified': rating is not None or rng.random() < 0.5},
        'score': fit, 'grade': fit, 'niche_fit': fit, 'checks': checks, 'deduction': 0, 'deduction_reasons': [],
        'rationale': '', 'notes': '', 'next_follow_up': None,
        'details': {'connects_cost': rng.choice((12, 13, 15, 16, 17)), 'brief': {'outcome': headline, 'scope': scope, 'requirements': [must]}},
    }


def build(today=None, seed=7):
    """The whole sample pipeline, oldest application first."""
    rng = random.Random(seed)
    today = today or datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    now = datetime.datetime.now(UTC)
    days = []
    for back, count in enumerate(reversed(WEEKS), start=1):
        start = monday - datetime.timedelta(weeks=back)
        days += [start + datetime.timedelta(days=rng.randrange(5)) for _ in range(count)]
    for offset in range(today.weekday() + 1):
        days += [monday + datetime.timedelta(days=offset)] * PER_DAY_NOW
    days.sort()

    jobs = []
    for n, day in enumerate(days):
        job = lead(n, rng)
        applied = datetime.datetime.combine(day, datetime.time(8, 0), UTC) + datetime.timedelta(minutes=rng.randrange(600))
        applied = min(applied, now - datetime.timedelta(minutes=5 + n % 40))
        speed = int(rng.choice((4, 6, 9, 12, 14, 15, 19, 26, 40, 75, 180)) * 60 * rng.uniform(0.8, 1.2))
        job.update({'posted_date': stamp(applied - datetime.timedelta(seconds=speed)), 'found_at': stamp(applied - datetime.timedelta(minutes=3)),
                    'applied_at': stamp(applied), 'applied_observation': {'verified': True, 'source': 'upwork-proposal'},
                    'speed_to_lead_s': speed, 'status': 'applied', 'status_updated_at': stamp(applied), 'last_activity_at': stamp(applied),
                    'history': [{'status': 'new', 'at': stamp(applied - datetime.timedelta(minutes=3))}, {'status': 'applied', 'at': stamp(applied)}],
                    '_applied': applied})
        jobs.append(job)

    def move(job, status, after, low, high):
        when = min(after + datetime.timedelta(hours=rng.uniform(low, high)), now - datetime.timedelta(minutes=rng.randrange(5, 240)))
        job['history'].append({'status': status, 'at': stamp(when)})
        job.update(status=status, status_updated_at=stamp(when), last_activity_at=stamp(when))
        return when

    old = [j for j in jobs if (today - j['_applied'].date()).days >= 7]
    recent = [j for j in jobs if 1 <= (today - j['_applied'].date()).days < 7]
    answered = rng.sample(old, 52) + rng.sample(recent, 6)
    plan = ['won'] * 21 + ['offer'] * 3 + ['call'] * 6 + ['lost'] * 14 + ['replied'] * 14
    for index, (job, end) in enumerate(zip(answered, plan)):
        replied = move(job, 'replied', job['_applied'], 1, 60)
        job.update(replied_at=stamp(replied), replied_observation={'verified': True, 'source': 'upwork-thread'})
        last = replied
        if end in ('won', 'offer', 'call') and not (end == 'won' and index % 4 == 3) or (end == 'lost' and index % 2):
            last = move(job, 'call', last, 12, 72)
            if end == 'call':
                job['call_at'] = (today + datetime.timedelta(days=index % 3 - 1)).isoformat()
        if end in ('won', 'offer'):
            last = move(job, 'offer', last, 6, 60)
        if end == 'won':
            won = move(job, 'won', last, 6, 72)
            if index >= 3:   # the newest three still need their handover written
                job.update(follow_up_plan={'lane': 'reactivation'}, next_follow_up=(won.date() + datetime.timedelta(days=60)).isoformat())
        elif end == 'lost':
            move(job, 'lost', last, 48, 240)
        elif end == 'replied':
            job['next_follow_up'] = (today + datetime.timedelta(days=index % 4 - 1)).isoformat()
    for job in jobs:
        applied = job.pop('_applied')
        if job['status'] == 'applied' and (today - applied.date()).days > 14:
            job['history'].append({'status': 'lost', 'at': stamp(applied + datetime.timedelta(days=14))})
            job.update(status='lost', status_updated_at=stamp(applied + datetime.timedelta(days=14)))

    for k in range(8):   # found this morning, not sent yet
        job = lead(len(days) + k, rng)
        found = now - datetime.timedelta(minutes=20 + 55 * k)
        job.update({'posted_date': stamp(found - datetime.timedelta(minutes=rng.randrange(3, 40))), 'found_at': stamp(found), 'status': 'new',
                    'status_updated_at': stamp(found), 'last_activity_at': stamp(found), 'history': [{'status': 'new', 'at': stamp(found)}]})
        jobs.append(job)
    return jobs


def beside(own, samples, sends=2):
    """The member's own leads with the sample history behind them, for a demo on a real list.

    Their pipeline is read here and never written: the result goes to the demo folder.
    The sample leads still to decide on are left out, so the Unsent pile is the member's
    own, and the Sent pile holds just `sends` sample applications; the other unanswered
    samples close as lost, which keeps them in the funnel and off the list.
    """
    now = stamp(datetime.datetime.now(UTC))
    samples = [job for job in samples if job['status'] != 'new']
    waiting = [job for job in samples if job['status'] == 'applied']
    for job in waiting[:-sends] if sends else waiting:
        job['history'].append({'status': 'lost', 'at': now})
        job.update(status='lost', status_updated_at=now)
    return list(own) + samples


def write(folder=None, own=None):
    """Write the sample pipeline and a fresh sync stamp. Returns the folder.

    `own` is the path of the member's real pipeline to show beside the samples.
    """
    folder = pathlib.Path(folder or ROOT / 'data' / 'demo')
    (folder / 'jobs').mkdir(parents=True, exist_ok=True)
    jobs = build()
    if own and pathlib.Path(own).is_file():
        jobs = beside(json.loads(pathlib.Path(own).read_text(encoding='utf-8')), jobs)
    (folder / 'jobs.json').write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding='utf-8')
    (folder / 'sync.json').write_text(json.dumps({'synced_at': datetime.datetime.now(UTC).isoformat()}), encoding='utf-8')
    return folder


if __name__ == '__main__':
    print(write(sys.argv[1] if len(sys.argv) > 1 else None))
