import { SHARED_FIELD_NAMES, TEMPLATES } from '../templates.js';

import { MessageForm } from './MessageForm.js';
import { MessagePreview } from './MessagePreview.js';
import { SharedFields } from './SharedFields.js';
import { StepIndicator } from './StepIndicator.js';
import { TemplateCards } from './TemplateCards.js';

import htm from 'htm';
import { createElement, useCallback, useEffect, useReducer } from 'react';

const html = htm.bind(createElement);

function initialFieldValues({ careerUrlDefault, resumeUrlDefault }) {
  const values = {};
  if (careerUrlDefault) values.careerUrl = careerUrlDefault;
  if (resumeUrlDefault) values.resumeUrl = resumeUrlDefault;
  return values;
}

function defaultsFor(template) {
  const values = {};
  for (const f of template.fields) {
    if (f.default !== undefined) {
      values[f.name] = f.default;
    }
  }
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
    case 'SELECT_TEMPLATE': {
      const template = TEMPLATES.find((t) => t.id === action.templateId);
      const merged = { ...defaultsFor(template), ...state.fieldValues };
      return {
        ...state,
        selectedTemplateId: action.templateId,
        fieldValues: merged,
        currentStep: 1,
      };
    }
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

export function App({ careerUrlDefault, resumeUrlDefault } = {}) {
  const [state, dispatch] = useReducer(reducer, {
    currentStep: 0,
    selectedTemplateId: null,
    fieldValues: initialFieldValues({ careerUrlDefault, resumeUrlDefault }),
  });

  // Restore from hash on mount
  useEffect(() => {
    const id = window.location.hash.replace(/^#/, '');
    if (id && TEMPLATES.some((t) => t.id === id)) {
      dispatch({ type: 'SELECT_TEMPLATE', templateId: id });
    }
  }, []);

  const handleSelectTemplate = useCallback((id) => {
    window.location.hash = id;
    dispatch({ type: 'SELECT_TEMPLATE', templateId: id });
  }, []);

  const handleGoBack = useCallback(() => {
    window.location.hash = '';
    dispatch({ type: 'GO_BACK' });
  }, []);

  const setField = useCallback((field, value) => dispatch({ type: 'SET_FIELD', field, value }), []);

  const selectedTemplate = TEMPLATES.find((t) => t.id === state.selectedTemplateId);

  return html`
    <div className="container py-4">
      <${StepIndicator} currentStep=${state.currentStep} />
      ${
        state.currentStep === 0 &&
        html`
          <${SharedFields} fieldValues=${state.fieldValues} onChange=${setField} />
          <${TemplateCards} templates=${TEMPLATES} sharedFieldValues=${state.fieldValues} onSelect=${handleSelectTemplate} />
        `
      }
      ${
        state.currentStep === 1 &&
        selectedTemplate &&
        html`
          <div className="row mt-4">
            <div className="col-lg-5 mb-3">
              <${MessageForm} template=${selectedTemplate} fieldValues=${state.fieldValues} onChange=${setField} />
              <button className="btn btn-outline-secondary mt-3" onClick=${handleGoBack}>← Back to templates</button>
            </div>
            <div className="col-lg-7">
              <${MessagePreview} template=${selectedTemplate} fieldValues=${state.fieldValues} />
            </div>
          </div>
        `
      }
    </div>
  `;
}
