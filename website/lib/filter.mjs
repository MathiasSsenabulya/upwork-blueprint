// The member's own job filter, as the dashboard shows it and as /find-jobs reads it.
// The dashboard never writes the filter: it builds one line to copy, and `python3 code/jobs.py
// filter` is the one writer, into context/me.md. The keys and values here are the ones
// that script accepts and hands back in /api/state, so change both together.
export const FILTER_FIELDS = [
  { key: 'bids', label: 'Bids already in', other: value => `Up to ${value}`, options: [['none', 'Any number'], ['5', 'Up to 5'], ['10', 'Up to 10'], ['20', 'Up to 20'], ['50', 'Up to 50']] },
  { key: 'posted', label: 'Posted within', other: value => `${String(value).replace(/h$/, '')} hours`, options: [['6h', '6 hours'], ['12h', '12 hours'], ['24h', '24 hours'], ['48h', '48 hours']] },
  { key: 'full-time', label: 'Full-time roles', options: [['hide', 'Hide'], ['show', 'Show']] },
  { key: 'rating', label: 'Client rating', other: value => `${value} and up`, options: [['none', 'Any rating'], ['3', '3.0 and up'], ['4', '4.0 and up'], ['4.5', '4.5 and up']] },
  { key: 'unverified', label: 'Unverified clients', options: [['hide', 'Hide'], ['show', 'Show, marked']] },
  { key: 'hourly', label: 'Hourly pay', other: value => `${value} of my rate and up`, options: [['none', 'Any rate'], ['50%', '50% of my rate and up'], ['60%', '60% of my rate and up'], ['80%', '80% of my rate and up']] },
  { key: 'fixed', label: 'Fixed price', other: value => `$${value} and up`, options: [['none', 'Any budget'], ['100', '$100 and up'], ['250', '$250 and up'], ['500', '$500 and up'], ['1000', '$1,000 and up']] },
];

/** A field's choices, with the saved value added when it is one the list does not offer. */
export function optionsFor(field, value) {
  if (value == null || field.options.some(([option]) => option === value)) return field.options;
  return [...field.options, [value, field.other ? field.other(value) : String(value)]];
}

/** The one line to paste into Claude Code. */
export function filterCommand(values) {
  return `/find-jobs filter ${FILTER_FIELDS.map(field => `${field.key}=${values[field.key]}`).join(' ')}`;
}
