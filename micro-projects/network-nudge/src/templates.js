// Fields shared across all templates — filled once, used everywhere.
// Names must match field definitions in each template's fields array.
// Default values come from the App component props (injected by the Jekyll page).
export const SHARED_FIELD_NAMES = ['recipientName', 'roleUrl', 'careerUrl', 'resumeUrl'];

const sharedFields = [
  { name: 'careerUrl', label: 'Career ChangeLog URL', type: 'url' },
  { name: 'resumeUrl', label: 'Resume URL', type: 'url' },
];

// Shared preview rendering — used by both TemplateCard and MessagePreview.
// Builds a values object from template fields, substituting [label] for missing values.
export function renderPreview(template, fieldValues) {
  const values = {};
  for (const f of template.fields) {
    values[f.name] = fieldValues[f.name] || `[${f.label}]`;
  }
  try {
    return template.render(values);
  } catch {
    return '';
  }
}

export const TEMPLATES = [
  {
    id: 'direct-application',
    title: 'Direct cold application',
    description: 'You found a role and want to reach the hiring manager or talent team directly.',
    linkedinLimit: true,
    fields: [{ name: 'recipientName', label: 'Recipient name', type: 'text' }, { name: 'roleUrl', label: 'Role URL', type: 'url' }, ...sharedFields],
    render: ({ recipientName, roleUrl, careerUrl, resumeUrl }) =>
      `Hi ${recipientName}!\n\nI came across ${roleUrl} and I believe I'd be a good fit for the role.\n\nMy background is at ${careerUrl} and my latest résumé is at ${resumeUrl}.\n\nAre you available to chat?`,
  },
  {
    id: 'cold-reachout',
    title: 'Cold reach-out with company',
    description: 'You are connecting with people at a specific company about a role.',
    linkedinLimit: true,
    fields: [
      { name: 'recipientName', label: 'Recipient name', type: 'text' },
      { name: 'companyName', label: 'Company name', type: 'text' },
      { name: 'roleUrl', label: 'Role URL', type: 'url' },
      ...sharedFields,
    ],
    render: ({ recipientName, companyName, roleUrl, careerUrl, resumeUrl }) =>
      `Hi ${recipientName}!\n\nI'm connecting with people at ${companyName} for this role:\n${roleUrl}\n\nMy background is at ${careerUrl} and my latest résumé is at ${resumeUrl}.\n\nAre you available for a chat?`,
  },
  {
    id: 'mutual-intro',
    title: 'Mutual intro request',
    description: 'You found someone at a target company — ask a mutual connection to introduce you.',
    linkedinLimit: false,
    fields: [
      { name: 'recipientName', label: 'Recipient name', type: 'text' },
      { name: 'targetName', label: 'Target person name', type: 'text' },
      { name: 'targetLinkedInUrl', label: 'Target person LinkedIn URL', type: 'url' },
      { name: 'companyName', label: 'Company name', type: 'text' },
      { name: 'roleUrl', label: 'Role URL', type: 'url' },
      { name: 'pronoun', label: 'Their pronoun', type: 'radio', options: ['him', 'her', 'them'] },
      ...sharedFields,
    ],
    render: ({ recipientName, targetName, targetLinkedInUrl, companyName, roleUrl, pronoun, careerUrl, resumeUrl }) =>
      `Hi ${recipientName}!\n\nI saw you're connected with ${targetName} (${targetLinkedInUrl}).\n\nI'm trying to create connections with people at ${companyName} for this role:\n${roleUrl}\n\nWould you be comfortable introducing me to ${pronoun} through either email or LinkedIn chat?\n\nMy background is at ${careerUrl} and my latest résumé is at ${resumeUrl}.\n\nThanks in advance!`,
  },
];
