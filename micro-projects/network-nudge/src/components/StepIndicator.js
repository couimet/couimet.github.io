import { MessageCode } from '../i18n/messageCodes.js';
import { useLocale } from '../i18n/supportedLocales.js';

import htm from 'htm';
import { createElement } from 'react';

const html = htm.bind(createElement);

export function StepIndicator({ currentStep }) {
  const { t } = useLocale();
  const steps = [t(MessageCode.STEP_CHOOSE_TEMPLATE), t(MessageCode.STEP_FILL_IN_COPY)];
  return html`
    <div className="d-flex justify-content-center mb-4">
      ${steps.map(
        (label, i) => html`
          <div key=${i} className="d-flex align-items-center">
            <div
              className="rounded-circle d-flex align-items-center justify-content-center me-2"
              style=${{
                width: '32px',
                height: '32px',
                backgroundColor: i <= currentStep ? 'var(--bs-primary, #0d6efd)' : '#dee2e6',
                color: i <= currentStep ? '#fff' : '#6c757d',
                fontWeight: 'bold',
                fontSize: '14px',
              }}
            >
              ${i + 1}
            </div>
            <span className=${i <= currentStep ? 'fw-semibold' : 'text-muted'}>${label}</span>
            ${i < steps.length - 1 && html`<div className="mx-3" style=${{ width: '40px', height: '2px', backgroundColor: i < currentStep ? 'var(--bs-primary, #0d6efd)' : '#dee2e6' }} />`}
          </div>
        `,
      )}
    </div>
  `;
}
