import { MessageCode } from '../i18n/messageCodes.js';
import { detectLocale, getMessages, LocaleContext, setLocale, supportedLocales } from '../i18n/supportedLocales.js';
import { SHARED_FIELD_NAMES, TEMPLATES } from '../templates.js';

import { MessageForm } from './MessageForm.js';
import { MessagePreview } from './MessagePreview.js';
import { SharedFields } from './SharedFields.js';
import { StepIndicator } from './StepIndicator.js';
import { TemplateCards } from './TemplateCards.js';

import htm from 'htm';
import { createElement, useCallback, useEffect, useReducer, useState } from 'react';

const html = htm.bind(createElement);

function initialFieldValues({ careerUrlDefault, resumeUrlDefault }) {
  const values = {};
  if (careerUrlDefault) values.careerUrl = careerUrlDefault;
  if (resumeUrlDefault) values.resumeUrl = resumeUrlDefault;
  return values;
}

function sharedValues(fieldValues) {
  const values = {};
  for (const name of SHARED_FIELD_NAMES) {
    if (fieldValues[name]) {
      values[name] = fieldValues[name];
    }
  }
  return values;
}

function reducer(state, action) {
  switch (action.type) {
    case 'SELECT_TEMPLATE':
      return {
        ...state,
        selectedTemplateId: action.templateId,
        fieldValues: state.fieldValues,
        currentStep: 1,
      };
    case 'SET_FIELD':
      return {
        ...state,
        fieldValues: { ...state.fieldValues, [action.field]: action.value },
      };
    case 'GO_BACK':
      return { ...state, currentStep: 0, selectedTemplateId: null, fieldValues: sharedValues(state.fieldValues) };
    default:
      return state;
  }
}

// Parse #<locale> or #<locale>--<templateId>. Returns { locale, templateId }.
// A plain #<templateId> (no --, first segment not a locale) is backward-compat:
// templateId is set and locale falls through to the detection chain.
function parseHash(hash) {
  const raw = hash.replace(/^#/, '');
  if (!raw) return { locale: null, templateId: null };
  const SEP = '--';
  const idx = raw.indexOf(SEP);
  const first = idx === -1 ? raw : raw.slice(0, idx);
  if (Object.hasOwn(supportedLocales, first)) {
    return { locale: first, templateId: idx === -1 ? null : raw.slice(idx + SEP.length) || null };
  }
  // No locale prefix — entire hash is a template ID (backward compat).
  return { locale: null, templateId: raw };
}

function buildHash(locale, templateId) {
  return templateId ? `#${locale}--${templateId}` : `#${locale}`;
}

export function App({ careerUrlDefault, resumeUrlDefault } = {}) {
  const [state, dispatch] = useReducer(reducer, {
    currentStep: 0,
    selectedTemplateId: null,
    fieldValues: initialFieldValues({ careerUrlDefault, resumeUrlDefault }),
  });

  // Lazy initializer: sync module-level locale before the first render so
  // getMessages() returns the correct bundle when children call renderPreview().
  const [locale, setLocaleState] = useState(() => {
    const { locale: hashLocale } = parseHash(window.location.hash);
    const resolved = hashLocale || detectLocale();
    setLocale(resolved);
    return resolved;
  });

  // Restore from hash on mount (locale may already be set from the lazy initializer above).
  useEffect(() => {
    const { templateId } = parseHash(window.location.hash);
    if (templateId && TEMPLATES.some((t) => t.id === templateId)) {
      dispatch({ type: 'SELECT_TEMPLATE', templateId });
    }
  }, []);

  // Updates the module-level locale (and localStorage) via supportedLocales,
  // then triggers a re-render through App's own state. Keeps the hash in sync.
  const handleSetLocale = useCallback(
    (newLocale) => {
      setLocale(newLocale);
      setLocaleState(newLocale);
      window.location.hash = buildHash(newLocale, state.selectedTemplateId);
    },
    [state.selectedTemplateId],
  );

  const handleSelectTemplate = useCallback(
    (id) => {
      window.location.hash = buildHash(locale, id);
      dispatch({ type: 'SELECT_TEMPLATE', templateId: id });
    },
    [locale],
  );

  const handleGoBack = useCallback(() => {
    window.location.hash = locale;
    dispatch({ type: 'GO_BACK' });
  }, [locale]);

  const setField = useCallback((field, value) => dispatch({ type: 'SET_FIELD', field, value }), []);

  const selectedTemplate = TEMPLATES.find((t) => t.id === state.selectedTemplateId);

  return html`
    <${LocaleContext.Provider} value=${{ locale, setLocale: handleSetLocale }}>
      <div className="container py-4">
        <div className="d-flex gap-2 mb-3">
          <button className=${`btn btn-sm ${locale === 'en' ? 'btn-primary' : 'btn-outline-secondary'}`} onClick=${() => handleSetLocale('en')}>EN</button>
          <button className=${`btn btn-sm ${locale === 'fr' ? 'btn-primary' : 'btn-outline-secondary'}`} onClick=${() => handleSetLocale('fr')}>FR</button>
        </div>
        <${StepIndicator} currentStep=${state.currentStep} />
        ${
          state.currentStep === 0 &&
          html`
            <${SharedFields} fieldValues=${state.fieldValues} onChange=${setField} />
            <${TemplateCards} templates=${TEMPLATES} sharedFieldValues=${state.fieldValues} onSelect=${handleSelectTemplate} locale=${locale} />
          `
        }
        ${
          state.currentStep === 1 &&
          selectedTemplate &&
          html`
            <div className="row mt-4">
              <div className="col-lg-5 mb-3">
                <${MessageForm} template=${selectedTemplate} fieldValues=${state.fieldValues} onChange=${setField} />
                <button className="btn btn-outline-secondary mt-3" onClick=${handleGoBack}>${getMessages()[MessageCode.BUTTON_BACK_TO_TEMPLATES]}</button>
              </div>
              <div className="col-lg-7">
                <${MessagePreview} template=${selectedTemplate} fieldValues=${state.fieldValues} locale=${locale} />
              </div>
            </div>
          `
        }
      </div>
    <//>
  `;
}
