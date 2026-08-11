// English translations for Network Nudge.
// Every MessageCode key has a non-empty string value.
// Dynamic interpolation uses {paramName} syntax.
import { MessageCode } from './messageCodes.js';

export const messagesEn = {
  // Step indicator
  [MessageCode.STEP_CHOOSE_TEMPLATE]: 'Choose template',
  [MessageCode.STEP_FILL_IN_COPY]: 'Fill in & copy',

  // Shared field labels
  [MessageCode.FIELD_RECIPIENT_NAME]: 'Recipient name',
  [MessageCode.FIELD_ROLE_URL]: 'Role URL',
  [MessageCode.FIELD_CAREER_URL]: 'Career ChangeLog URL',
  [MessageCode.FIELD_RESUME_URL]: 'Resume URL',
  [MessageCode.FIELD_COMPANY_NAME]: 'Company name',
  [MessageCode.FIELD_TARGET_NAME]: 'Target person name',
  [MessageCode.FIELD_TARGET_LINKEDIN_URL]: 'Target person LinkedIn URL',
  [MessageCode.FIELD_PRONOUN]: 'Their pronoun',

  // Pronoun display values (for radio button labels)
  [MessageCode.PRONOUN_HIM]: 'him',
  [MessageCode.PRONOUN_HER]: 'her',
  [MessageCode.PRONOUN_THEM]: 'them',

  // Template titles
  [MessageCode.TEMPLATE_DIRECT_APPLICATION_TITLE]: 'Direct cold application',
  [MessageCode.TEMPLATE_COLD_REACHOUT_TITLE]: 'Cold reach-out with company',
  [MessageCode.TEMPLATE_MUTUAL_INTRO_TITLE]: 'Mutual intro request',

  // Template descriptions
  [MessageCode.TEMPLATE_DIRECT_APPLICATION_DESC]: 'You found a role and want to reach the hiring manager or talent team directly.',
  [MessageCode.TEMPLATE_COLD_REACHOUT_DESC]: 'You are connecting with people at a specific company about a role.',
  [MessageCode.TEMPLATE_MUTUAL_INTRO_DESC]: 'You found someone at a target company — ask a mutual connection to introduce you.',

  // Template message bodies (use {param} interpolation)
  [MessageCode.TEMPLATE_DIRECT_APPLICATION_BODY]:
    "Hi {recipientName}!\n\nI came across {roleUrl} and I believe I'd be a good fit for the role.\n\nBackground: {careerUrl}\nRésumé: {resumeUrl}\n\nAre you available to chat?",
  [MessageCode.TEMPLATE_COLD_REACHOUT_BODY]:
    "Hi {recipientName}!\n\nI'm connecting with people at {companyName} for this role:\n{roleUrl}\n\nBackground: {careerUrl}\nRésumé: {resumeUrl}\n\nAre you available to chat?",
  [MessageCode.TEMPLATE_MUTUAL_INTRO_BODY]:
    "Hi {recipientName}!\n\nI saw you're connected with {targetName} ({targetLinkedInUrl}).\n\nI'm trying to create connections with people at {companyName} for this role:\n{roleUrl}\n\nWould you be comfortable introducing me to {pronoun} through either email or LinkedIn chat?\n\nBackground: {careerUrl}\nRésumé: {resumeUrl}\n\nThanks in advance!",

  // Preview
  [MessageCode.PREVIEW_HEADING]: 'Preview',
  [MessageCode.PREVIEW_MISSING]: 'Missing: {missing}',
  [MessageCode.PREVIEW_RESET_TO_TEMPLATE]: 'Reset to template',
  [MessageCode.PREVIEW_CHARACTER]: '{count}{limit} character',
  [MessageCode.PREVIEW_CHARACTERS]: '{count}{limit} characters',
  [MessageCode.PREVIEW_OVER_LIMIT]: '— over LinkedIn limit!',
  [MessageCode.PREVIEW_COPY_TO_CLIPBOARD]: 'Copy to clipboard',
  [MessageCode.PREVIEW_COPIED]: 'Copied!',
  [MessageCode.PREVIEW_FILL_IN_TITLE]: 'Fill in: {missing}',

  // Buttons
  [MessageCode.BUTTON_SELECT]: 'Select',
  [MessageCode.BUTTON_BACK_TO_TEMPLATES]: '← Back to templates',
  [MessageCode.TITLE_COPY_TO_CLIPBOARD]: 'Copy to clipboard',
};
