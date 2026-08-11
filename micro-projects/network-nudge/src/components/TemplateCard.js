import { MessageCode } from '../i18n/messageCodes.js';
import { useLocale } from '../i18n/supportedLocales.js';
import { renderPreview } from '../templates.js';

import htm from 'htm';
import { createElement, useCallback, useEffect, useMemo, useRef, useState } from 'react';

const html = htm.bind(createElement);

export function TemplateCard({ template, sharedFieldValues, onSelect }) {
  const { locale, t } = useLocale();
  const [copied, setCopied] = useState(false);
  const timeoutRef = useRef(null);

  const preview = useMemo(() => renderPreview(template, sharedFieldValues), [template, sharedFieldValues, locale]);

  const isComplete = !preview.includes('[');

  // Clear copy-feedback timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const handleCopy = useCallback(
    async (e) => {
      e.stopPropagation();
      try {
        await navigator.clipboard.writeText(preview);
        setCopied(true);
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        timeoutRef.current = setTimeout(() => setCopied(false), 2000);
      } catch {
        // clipboard unavailable — no-op
      }
    },
    [preview],
  );

  return html`
    <div className="card h-100" style=${{ cursor: 'pointer' }} onClick=${onSelect}>
      <div className="card-body d-flex flex-column">
        <h5 className="card-title mb-1">${t(template.titleCode)}</h5>
        <p className="card-text mb-3" style=${{ fontSize: '0.8rem', color: '#adb5bd', fontStyle: 'italic' }}>${t(template.descCode)}</p>
        <div className="flex-grow-1 position-relative" style=${{ borderLeft: '3px solid #dee2e6', paddingLeft: '14px', marginLeft: '2px' }}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="22"
            height="22"
            fill="#dee2e6"
            viewBox="0 0 16 16"
            style=${{ position: 'absolute', top: '-2px', left: '-13px' }}
          >
            <path
              d="M12 12a1 1 0 0 0 1-1V8.558a1 1 0 0 0-1-1h-1.388c0-.351.021-.703.062-1.054.062-.372.166-.703.31-.992.145-.29.331-.517.559-.683.227-.186.516-.279.868-.279V3c-.579 0-1.085.124-1.52.372a3.322 3.322 0 0 0-1.085.992 4.92 4.92 0 0 0-.62 1.458A7.712 7.712 0 0 0 9 7.558V11a1 1 0 0 0 1 1h2Zm-6 0a1 1 0 0 0 1-1V8.558a1 1 0 0 0-1-1H4.612c0-.351.021-.703.062-1.054.062-.372.166-.703.31-.992.145-.29.331-.517.559-.683.227-.186.516-.279.868-.279V3c-.579 0-1.085.124-1.52.372a3.322 3.322 0 0 0-1.085.992 4.92 4.92 0 0 0-.62 1.458A7.712 7.712 0 0 0 3 7.558V11a1 1 0 0 0 1 1h2Z"
            />
          </svg>
          <pre
            className="mb-0"
            style=${{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: '0.875rem', color: '#212529', background: 'none', border: 'none', padding: 0 }}
          >
${preview}</pre>
        </div>
      </div>
      <div className="card-footer d-flex gap-2">
        <button className="btn btn-primary btn-sm flex-grow-1">${t(MessageCode.BUTTON_SELECT)}</button>
        ${
          isComplete &&
          html`
            <button
              className=${`btn btn-sm ${copied ? 'btn-success' : 'btn-outline-secondary'}`}
              onClick=${handleCopy}
              title=${t(MessageCode.TITLE_COPY_TO_CLIPBOARD)}
            >
              ${
                copied
                  ? t(MessageCode.PREVIEW_COPIED)
                  : html`<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"
                      />
                      <path
                        d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z"
                      />
                    </svg>`
              }
            </button>
          `
        }
      </div>
    </div>
  `;
}
