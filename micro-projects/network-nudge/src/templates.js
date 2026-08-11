// Fields shared across all templates — filled once, used everywhere.
// Names must match field definitions in each template's fields array.
// Default values come from the App component props (injected by the Jekyll page).

import { MessageCode } from './i18n/messageCodes.js';
import { format, getMessages } from './i18n/supportedLocales.js';

export const SHARED_FIELD_NAMES = ['recipientName', 'roleUrl', 'careerUrl', 'resumeUrl'];

// Internal pronoun values (language-neutral keys). Display labels come from
// i18n (PRONOUN_HIM/HER/THEM). Template bodies use {pronoun} — the rendering
// code resolves the internal value through the i18n messages before format().
export const PRONOUN_OPTIONS = ['him', 'her', 'them'];

const PRONOUN_CODE_MAP = {
  him: MessageCode.PRONOUN_HIM,
  her: MessageCode.PRONOUN_HER,
  them: MessageCode.PRONOUN_THEM,
};

const sharedFields = [
  { name: 'careerUrl', labelCode: MessageCode.FIELD_CAREER_URL, type: 'url' },
  { name: 'resumeUrl', labelCode: MessageCode.FIELD_RESUME_URL, type: 'url' },
];

// Shared preview rendering — used by both TemplateCard and MessagePreview.
// Builds a values object from template fields, substituting [label] for missing values.
export function renderPreview(template, fieldValues) {
  const msgs = getMessages();
  const values = {};
  for (const f of template.fields) {
    values[f.name] = fieldValues[f.name] || `[${msgs[f.labelCode] || f.name}]`;
  }
  try {
    const msg = msgs[template.messageCode];
    const params = { ...values, pronoun: msgs[PRONOUN_CODE_MAP[values.pronoun]] || values.pronoun || '' };
    return format(msg, params);
  } catch {
    return '';
  }
}

export const TEMPLATES = [
  {
    id: 'direct-application',
    titleCode: MessageCode.TEMPLATE_DIRECT_APPLICATION_TITLE,
    descCode: MessageCode.TEMPLATE_DIRECT_APPLICATION_DESC,
    linkedinLimit: true,
    messageCode: MessageCode.TEMPLATE_DIRECT_APPLICATION_BODY,
    fields: [
      { name: 'recipientName', labelCode: MessageCode.FIELD_RECIPIENT_NAME, type: 'text' },
      { name: 'roleUrl', labelCode: MessageCode.FIELD_ROLE_URL, type: 'url' },
      ...sharedFields,
    ],
  },
  {
    id: 'cold-reachout',
    titleCode: MessageCode.TEMPLATE_COLD_REACHOUT_TITLE,
    descCode: MessageCode.TEMPLATE_COLD_REACHOUT_DESC,
    linkedinLimit: true,
    messageCode: MessageCode.TEMPLATE_COLD_REACHOUT_BODY,
    fields: [
      { name: 'recipientName', labelCode: MessageCode.FIELD_RECIPIENT_NAME, type: 'text' },
      { name: 'companyName', labelCode: MessageCode.FIELD_COMPANY_NAME, type: 'text' },
      { name: 'roleUrl', labelCode: MessageCode.FIELD_ROLE_URL, type: 'url' },
      ...sharedFields,
    ],
  },
  {
    id: 'mutual-intro',
    titleCode: MessageCode.TEMPLATE_MUTUAL_INTRO_TITLE,
    descCode: MessageCode.TEMPLATE_MUTUAL_INTRO_DESC,
    linkedinLimit: false,
    messageCode: MessageCode.TEMPLATE_MUTUAL_INTRO_BODY,
    fields: [
      { name: 'recipientName', labelCode: MessageCode.FIELD_RECIPIENT_NAME, type: 'text' },
      { name: 'targetName', labelCode: MessageCode.FIELD_TARGET_NAME, type: 'text' },
      { name: 'targetLinkedInUrl', labelCode: MessageCode.FIELD_TARGET_LINKEDIN_URL, type: 'url' },
      { name: 'companyName', labelCode: MessageCode.FIELD_COMPANY_NAME, type: 'text' },
      { name: 'roleUrl', labelCode: MessageCode.FIELD_ROLE_URL, type: 'url' },
      { name: 'pronoun', labelCode: MessageCode.FIELD_PRONOUN, type: 'radio', options: PRONOUN_OPTIONS },
      ...sharedFields,
    ],
  },
];
