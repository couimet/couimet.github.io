import { MessageCode } from '../i18n/messageCodes.js';
import { useLocale } from '../i18n/supportedLocales.js';
import { PRONOUN_OPTIONS } from '../templates.js';

import htm from 'htm';
import { createElement, Fragment } from 'react';

const html = htm.bind(createElement);

// Radio option value → translation key for its display label ('him' → PRONOUN_HIM).
const PRONOUN_DISPLAY = Object.fromEntries(PRONOUN_OPTIONS.map((opt) => [opt, MessageCode[`PRONOUN_${opt.toUpperCase()}`]]));

export function MessageForm({ template, fieldValues, onChange }) {
  const { t } = useLocale();
  return html`
    <${Fragment}>
      <h5 className="mb-2">${t(template.titleCode)}</h5>
      <p className="text-muted mb-3"><small>${t(template.descCode)}</small></p>
      ${template.fields.map(
        (field) => html`
          <div key=${field.name} className="mb-3">
            <label htmlFor=${field.name} className="form-label">
              ${
                field.name === 'careerUrl'
                  ? (() => {
                      const label = t(MessageCode.FIELD_CAREER_URL);
                      const [before, after] = label.split('ChangeLog');
                      return html`${before}<code>ChangeLog</code>${after || ''}`;
                    })()
                  : t(field.labelCode)
              }
            </label>
            ${
              field.type === 'radio'
                ? html`
                    <div>
                      ${field.options.map(
                        (opt) => html`
                          <div key=${opt} className="form-check form-check-inline">
                            <input
                              className="form-check-input"
                              type="radio"
                              name=${field.name}
                              id=${`${field.name}-${opt}`}
                              value=${opt}
                              checked=${fieldValues[field.name] === opt}
                              onChange=${(e) => onChange(field.name, e.target.value)}
                            />
                            <label className="form-check-label" htmlFor=${`${field.name}-${opt}`}>${t(PRONOUN_DISPLAY[opt])}</label>
                          </div>
                        `,
                      )}
                    </div>
                  `
                : html`
                    <input
                      type=${field.type}
                      className="form-control"
                      id=${field.name}
                      value=${fieldValues[field.name] || ''}
                      onChange=${(e) => onChange(field.name, e.target.value)}
                      placeholder=${t(field.labelCode)}
                    />
                  `
            }
          </div>
        `,
      )}
    <//>
  `;
}
