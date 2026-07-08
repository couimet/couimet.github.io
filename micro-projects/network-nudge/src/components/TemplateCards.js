import { TemplateCard } from './TemplateCard.js';

import htm from 'htm';
import { createElement } from 'react';

const html = htm.bind(createElement);

export function TemplateCards({ templates, sharedFieldValues, onSelect }) {
  return html`
    <div className="row g-4">
      ${templates.map(
        (t) => html`
          <div key=${t.id} className="col-md-6 col-lg-4 d-flex">
            <${TemplateCard} template=${t} sharedFieldValues=${sharedFieldValues} onSelect=${() => onSelect(t.id)} />
          </div>
        `,
      )}
    </div>
  `;
}
