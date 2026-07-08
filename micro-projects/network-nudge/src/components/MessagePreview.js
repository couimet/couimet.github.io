import htm from 'htm';
import { createElement, Fragment, useEffect, useMemo, useState } from 'react';

const LINKEDIN_CHAR_LIMIT = 300;

const html = htm.bind(createElement);

function fieldsWithValues(template, fieldValues) {
  return template.fields.map((f) => ({
    ...f,
    value: fieldValues[f.name] || '',
  }));
}

function missingFieldLabels(fields) {
  return fields.filter((f) => !f.value).map((f) => f.label);
}

function renderMessage(template, fieldValues) {
  const fields = fieldsWithValues(template, fieldValues);
  const filled = Object.fromEntries(fields.map((f) => [f.name, f.value || `[${f.label}]`]));
  try {
    return template.render(filled);
  } catch {
    return '';
  }
}

export function MessagePreview({ template, fieldValues }) {
  const [copied, setCopied] = useState(false);
  const [editedMessage, setEditedMessage] = useState(null);
  const [hasEdited, setHasEdited] = useState(false);

  const generatedMessage = useMemo(() => renderMessage(template, fieldValues), [template, fieldValues]);

  const message = hasEdited ? editedMessage : generatedMessage;

  const missing = useMemo(() => missingFieldLabels(fieldsWithValues(template, fieldValues)), [template, fieldValues]);

  const charCount = message.length;
  const limitEnabled = template.linkedinLimit !== false;
  const overLimit = limitEnabled && charCount > LINKEDIN_CHAR_LIMIT;
  const hasMissing = missing.length > 0;

  // Reset user edits when a different template is selected
  useEffect(() => {
    setEditedMessage(null);
    setHasEdited(false);
  }, [template.id]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard unavailable — no-op
    }
  };

  const handleChange = (e) => {
    setEditedMessage(e.target.value);
    setHasEdited(true);
  };

  const handleReset = () => {
    setEditedMessage(null);
    setHasEdited(false);
  };

  return html`
    <${Fragment}>
      <h5 className="mb-2">Preview</h5>
      ${
        hasMissing &&
        html`
          <div className="alert alert-warning py-2 mb-2">
            <small> Missing: ${missing.join(', ')} </small>
          </div>
        `
      }
      <textarea
        className=${`form-control mb-2${hasMissing ? ' border-warning' : ''}`}
        rows="10"
        value=${message}
        onChange=${handleChange}
        style=${{
          resize: 'vertical',
          fontFamily: 'inherit',
          backgroundColor: hasMissing ? '#fff9e6' : undefined,
        }}
      />
      ${
        hasEdited &&
        html`
          <div className="d-flex justify-content-center mb-2">
            <button className="btn btn-sm btn-link text-decoration-none p-0" onClick=${handleReset}>Reset to template</button>
          </div>
        `
      }
      <div className="d-flex justify-content-between align-items-center">
        <span className=${overLimit ? 'text-danger fw-bold' : 'text-muted'}>
          ${charCount}${limitEnabled ? ` / ${LINKEDIN_CHAR_LIMIT}` : ''} character${charCount !== 1 ? 's' : ''}${overLimit ? ' — over LinkedIn limit!' : ''}
        </span>
        <button
          className=${`btn btn-sm ${copied ? 'btn-success' : 'btn-outline-primary'}`}
          onClick=${handleCopy}
          disabled=${hasMissing}
          title=${hasMissing ? `Fill in: ${missing.join(', ')}` : 'Copy to clipboard'}
        >
          ${copied ? 'Copied!' : 'Copy to clipboard'}
        </button>
      </div>
    <//>
  `;
}
