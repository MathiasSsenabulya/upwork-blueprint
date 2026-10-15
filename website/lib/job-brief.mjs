const ACTION = /\b(build|set up|create|configure|connect|integrate|automate|fix|design|develop|implement|debug|review|map|test|document|train|sync|route|handle|notify|revoke|restore|track|analyse|analyze)\b/i;
const REQUIREMENT = /\b(must|mandatory|required|non-negotiable|do not apply|proven experience|should have|you should have|looking for someone experienced)\b/i;
// Old cached summaries sometimes appended the screener's recommendation to the
// client's requested outcome. Keep that text, but label it as a saved decision
// note instead of presenting it as something the client asked for.
const DECISION_NOTE = /(?:\bcrowded\b.*\bstand out\b|\bexact overlap\b.*\b(?:proof|work)\b|\b(?:worth|not worth) applying\b|\bnot a fit\b)/i;

function clean(value) {
  return String(value || '')
    .replace(/<\/?untrusted_participant_content>/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function list(value) {
  return Array.isArray(value) ? value.map(clean).filter(Boolean) : [];
}

function segments(value) {
  return String(value || '')
    .replace(/<\/?untrusted_participant_content>/g, '')
    .replace(/[•●▪]/g, '\n')
    .split(/\n+|(?<=[.!?])\s+(?=[A-Z])/)
    .map(line => clean(line).replace(/^(?:scope|tasks include|deliverables|what you(?:'ll| will) build)\s*:\s*/i, ''))
    .filter(line => line.length >= 20);
}

function splitOutcome(value) {
  const sentences = clean(value).split(/(?<=[.!?])\s+(?=[A-Z])/).filter(Boolean);
  const decision = sentences.filter(sentence => DECISION_NOTE.test(sentence)).join(' ');
  const outcome = sentences.filter(sentence => !DECISION_NOTE.test(sentence)).join(' ');
  return { outcome: outcome || (decision ? '' : clean(value)), decision };
}

// A row explains the work. Fit recommendations stay in the drawer and lead page.
export function jobPreview(job) {
  return deriveJobBrief(job).outcome || splitOutcome(job?.summary).outcome || 'Open this job to review the available details.';
}

export function deriveJobBrief(job) {
  const details = job?.details || {};
  const saved = details.brief || {};
  const savedOutcome = splitOutcome(saved.outcome);
  const savedScope = list(saved.scope);
  const savedRequirements = list(saved.requirements);
  if (savedOutcome.outcome || savedOutcome.decision || savedScope.length || savedRequirements.length) {
    return {
      outcome: savedOutcome.outcome,
      scope: savedScope,
      requirements: savedRequirements,
      ...(savedOutcome.decision ? { decision: savedOutcome.decision } : {}),
    };
  }

  const parts = segments(details.description);
  const fallbackOutcome = splitOutcome(clean(job?.summary) || parts[0] || '');
  const candidates = job?.summary ? parts.slice(1) : parts;
  const requirements = candidates.filter(line => REQUIREMENT.test(line));
  let scope = candidates.filter(line => ACTION.test(line) && !REQUIREMENT.test(line));
  if (!scope.length) scope = candidates.filter(line => !REQUIREMENT.test(line));

  return {
    outcome: fallbackOutcome.outcome,
    scope,
    requirements,
    ...(fallbackOutcome.decision ? { decision: fallbackOutcome.decision } : {}),
  };
}

const wordsOf = text => String(text || '').split(/\s+/).filter(Boolean);
function shorten(text, limit) {
  const words = wordsOf(text);
  return words.length <= limit ? words.join(' ').replace(/\.$/, '') : `${words.slice(0, limit).join(' ').replace(/[,;:.]$/, '')}…`;
}

/** The job in bullets, fifty words at most (12.10.2026). The headline above the panel
 * already says who wants what, so this lists the work and the hard must-haves and stops.
 * A brief as long as the posting saves nobody time, and the posting is one click away. */
export function briefBullets(job, limit = 50, each = 12) {
  const brief = deriveJobBrief(job);
  const picks = [...brief.scope.slice(0, 3), ...brief.requirements.slice(0, 2).map(item => `Must have: ${item}`)];
  if (!picks.length && brief.outcome) picks.push(brief.outcome.split(/(?<=[.!?])\s+(?=[A-Z])/)[0]);
  const bullets = [];
  let used = 0;
  for (const pick of picks) {
    const line = shorten(pick, each), count = wordsOf(line).length;
    if (used + count > limit) continue;
    bullets.push(line);
    used += count;
  }
  return bullets;
}
