import { MessageCode } from '../i18n/messageCodes.js';
import { format, supportedLocales, useLocale } from '../i18n/supportedLocales.js';
import { renderPreview } from '../templates.js';

import htm from 'htm';
import { createElement, Fragment, useEffect, useMemo, useRef, useState } from 'react';

const LINKEDIN_CHAR_LIMIT = 300;

const html = htm.bind(createElement);

function fieldsWithValues(template, fieldValues) {
  return template.fields.map((f) => ({
    ...f,
    value: fieldValues[f.name] || '',
  }));
}

function missingFieldLabels(fields, msgs) {
  return fields.filter((f) => !f.value).map((f) => msgs[f.labelCode] || f.labelCode);
}

export function MessagePreview({ template, fieldValues }) {
  const { locale, t } = useLocale();
  const [copied, setCopied] = useState(false);
  const [editedMessage, setEditedMessage] = useState(null);
  const [hasEdited, setHasEdited] = useState(false);
  const timeoutRef = useRef(null);

  const msgs = supportedLocales[locale];

  const generatedMessage = useMemo(() => renderPreview(template, fieldValues, msgs), [template, fieldValues, msgs]);

  const message = hasEdited ? editedMessage : generatedMessage;

  const missing = useMemo(() => missingFieldLabels(fieldsWithValues(template, fieldValues), msgs), [template, fieldValues, msgs]);

  const charCount = message.length;
  const limitEnabled = template.linkedinLimit !== false;
  const overLimit = limitEnabled && charCount > LINKEDIN_CHAR_LIMIT;
  const hasMissing = missing.length > 0;

  // Reset user edits when a different template is selected
  useEffect(() => {
    setEditedMessage(null);
    setHasEdited(false);
  }, [template.id]);

  // Clear copy-feedback timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message);
      setCopied(true);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => setCopied(false), 2000);
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
      <h5 className="mb-2">${t(MessageCode.PREVIEW_HEADING)}</h5>
      ${
        hasMissing &&
        html`
          <div className="alert alert-warning py-2 mb-2">
            <small> ${format(msgs[MessageCode.PREVIEW_MISSING], { missing: missing.join(', ') })} </small>
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
            <button className="btn btn-sm btn-link text-decoration-none p-0" onClick=${handleReset}>${t(MessageCode.PREVIEW_RESET_TO_TEMPLATE)}</button>
          </div>
        `
      }
      <div className="d-flex justify-content-between align-items-center">
        <span className=${overLimit ? 'text-danger fw-bold' : 'text-muted'}>
          ${format(msgs[charCount === 1 ? MessageCode.PREVIEW_CHARACTER : MessageCode.PREVIEW_CHARACTERS], { count: charCount, limit: limitEnabled ? ` / ${LINKEDIN_CHAR_LIMIT}` : '' })}${overLimit ? t(MessageCode.PREVIEW_OVER_LIMIT) : ''}
        </span>
        <button
          className=${`btn btn-sm ${copied ? 'btn-success' : 'btn-outline-primary'}`}
          onClick=${handleCopy}
          disabled=${hasMissing}
          title=${hasMissing ? format(msgs[MessageCode.PREVIEW_FILL_IN_TITLE], { missing: missing.join(', ') }) : t(MessageCode.PREVIEW_COPY_TO_CLIPBOARD)}
        >
          ${copied ? t(MessageCode.PREVIEW_COPIED) : t(MessageCode.PREVIEW_COPY_TO_CLIPBOARD)}
        </button>
      </div>
    <//>
  `;
}
