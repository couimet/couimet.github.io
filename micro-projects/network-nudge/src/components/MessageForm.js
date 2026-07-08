import htm from 'htm';
import { createElement, Fragment } from 'react';

const html = htm.bind(createElement);

export function MessageForm({ template, fieldValues, onChange }) {
  return html`
    <${Fragment}>
      <h5 className="mb-2">${template.title}</h5>
      <p className="text-muted mb-3"><small>${template.description}</small></p>
      ${template.fields.map(
        (field) => html`
          <div key=${field.name} className="mb-3">
            <label htmlFor=${field.name} className="form-label">
              ${field.name === 'careerUrl' ? html`<${Fragment}>Career <code>ChangeLog</code> URL<//>` : field.label}
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
                            <label className="form-check-label" htmlFor=${`${field.name}-${opt}`}>${opt}</label>
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
                      placeholder=${field.label}
                    />
                  `
            }
          </div>
        `,
      )}
    <//>
  `;
}
