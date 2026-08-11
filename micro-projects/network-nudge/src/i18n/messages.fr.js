import { MessageCode } from './messageCodes.js';

export const messagesFr = {
  // Step indicator
  [MessageCode.STEP_CHOOSE_TEMPLATE]: 'Choisir un modèle',
  [MessageCode.STEP_FILL_IN_COPY]: 'Remplir et copier',

  // Shared field labels
  [MessageCode.FIELD_RECIPIENT_NAME]: 'Nom du destinataire',
  [MessageCode.FIELD_ROLE_URL]: 'URL du poste',
  [MessageCode.FIELD_CAREER_URL]: 'URL du ChangeLog de carrière',
  [MessageCode.FIELD_RESUME_URL]: 'URL du CV',
  [MessageCode.FIELD_COMPANY_NAME]: "Nom de l'entreprise",
  [MessageCode.FIELD_TARGET_NAME]: 'Nom de la personne cible',
  [MessageCode.FIELD_TARGET_LINKEDIN_URL]: 'URL LinkedIn de la personne cible',
  [MessageCode.FIELD_PRONOUN]: 'Pronom',

  // Pronoun display values (for radio button labels)
  [MessageCode.PRONOUN_HIM]: 'lui',
  [MessageCode.PRONOUN_HER]: 'elle',
  [MessageCode.PRONOUN_THEM]: 'eux',

  // Template titles
  [MessageCode.TEMPLATE_DIRECT_APPLICATION_TITLE]: 'Candidature directe',
  [MessageCode.TEMPLATE_COLD_REACHOUT_TITLE]: "Contact direct avec l'entreprise",
  [MessageCode.TEMPLATE_MUTUAL_INTRO_TITLE]: "Demande d'introduction mutuelle",

  // Template descriptions
  [MessageCode.TEMPLATE_DIRECT_APPLICATION_DESC]:
    "Vous avez trouvé un poste et souhaitez contacter directement le responsable du recrutement ou l'équipe talent.",
  [MessageCode.TEMPLATE_COLD_REACHOUT_DESC]: "Vous prenez contact avec des personnes d'une entreprise précise à propos d'un poste.",
  [MessageCode.TEMPLATE_MUTUAL_INTRO_DESC]: "Vous avez trouvé une personne dans l'entreprise cible — demandez à une connaissance commune de vous présenter.",

  // Template message bodies (use {param} interpolation)
  [MessageCode.TEMPLATE_DIRECT_APPLICATION_BODY]:
    "Bonjour {recipientName} !\n\nJ'ai trouvé {roleUrl} et je pense que ce poste correspondrait bien à mon profil.\n\nParcours : {careerUrl}\nCV : {resumeUrl}\n\nDisponible pour en discuter ?",
  [MessageCode.TEMPLATE_COLD_REACHOUT_BODY]:
    'Bonjour {recipientName} !\n\nJe contacte des personnes chez {companyName} pour ce poste :\n{roleUrl}\n\nParcours : {careerUrl}\nCV : {resumeUrl}\n\nDisponible pour en discuter ?',
  [MessageCode.TEMPLATE_MUTUAL_INTRO_BODY]:
    "Bonjour {recipientName} !\n\nJe vois que vous êtes en contact avec {targetName} ({targetLinkedInUrl}).\n\nJe cherche à créer des liens avec des personnes chez {companyName} pour ce poste :\n{roleUrl}\n\nSeriez-vous à l'aise de me présenter à {pronoun} par courriel ou via LinkedIn ?\n\nParcours : {careerUrl}\nCV : {resumeUrl}\n\nMerci d'avance !",

  // Preview
  [MessageCode.PREVIEW_HEADING]: 'Aperçu',
  [MessageCode.PREVIEW_MISSING]: 'Champs manquants : {missing}',
  [MessageCode.PREVIEW_RESET_TO_TEMPLATE]: 'Revenir au modèle',
  [MessageCode.PREVIEW_CHARACTER]: '{count}{limit} caractère',
  [MessageCode.PREVIEW_CHARACTERS]: '{count}{limit} caractères',
  [MessageCode.PREVIEW_OVER_LIMIT]: ' — limite LinkedIn dépassée !',
  [MessageCode.PREVIEW_COPY_TO_CLIPBOARD]: 'Copier dans le presse-papiers',
  [MessageCode.PREVIEW_COPIED]: 'Copié !',
  [MessageCode.PREVIEW_FILL_IN_TITLE]: 'À remplir : {missing}',

  // Buttons
  [MessageCode.BUTTON_SELECT]: 'Sélectionner',
  [MessageCode.BUTTON_BACK_TO_TEMPLATES]: 'Retour aux modèles',
  [MessageCode.TITLE_COPY_TO_CLIPBOARD]: 'Copier dans le presse-papiers',
};
