import { MessageCode } from '../i18n/messageCodes.js';
import { useLocale } from '../i18n/supportedLocales.js';
import { SHARED_FIELD_NAMES, TEMPLATES } from '../templates.js';

import htm from 'htm';
import { createElement } from 'react';

const html = htm.bind(createElement);

// Pull field definitions from the first template (all templates share these).
const sharedDefs = TEMPLATES[0].fields.filter((f) => SHARED_FIELD_NAMES.includes(f.name));

const fieldWidths = {
  recipientName: 'col-md-6 col-lg-4',
  roleUrl: 'col-md-6 col-lg-8',
  careerUrl: 'col-md-6 col-lg-6',
  resumeUrl: 'col-md-6 col-lg-6',
};

export function SharedFields({ fieldValues, onChange }) {
  const { t } = useLocale();
  return html`
    <div className="row g-3 mb-4">
      ${sharedDefs.map(
        (field) => html`
          <div key=${field.name} className=${fieldWidths[field.name] || 'col-md-6 col-lg-3'}>
            <label htmlFor=${`shared-${field.name}`} className="form-label">
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
            <input
              type=${field.type}
              className="form-control"
              id=${`shared-${field.name}`}
              value=${fieldValues[field.name] || ''}
              onChange=${(e) => onChange(field.name, e.target.value)}
              placeholder=${t(field.labelCode)}
            />
          </div>
        `,
      )}
    </div>
  `;
}
