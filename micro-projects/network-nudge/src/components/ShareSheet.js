// Compose-view share sheet: a small anchored popover opened by
// the step-1 Share button that offers two flavors, named by the reader rather
// than the mechanism. The primary row is the current view pinned to its
// locale ("English, as you're using it") and copies /s/<pinnedShareIds[locale]>;
// the secondary row is "let the reader choose" and copies the same plain
// /s/<shareId> the template cards share. A row click copies the link, flips the
// row to the transient green "Link copied!" state, then dismisses. Built by
// hand (no Bootstrap dropdown JS): closes on click-outside and Escape and
// returns focus to the trigger.
import { MessageCode } from '../i18n/messageCodes.js';
import { useLocale } from '../i18n/supportedLocales.js';
import { useCopy } from '../useCopy.js';

import htm from 'htm';
import { createElement, useCallback, useEffect, useRef } from 'react';

const html = htm.bind(createElement);

const COPIED_DISMISS_MS = 1400;

export function ShareSheet({ template, onClose, triggerRef }) {
  const { locale, t } = useLocale();
  const sheetRef = useRef(null);
  const primaryRowRef = useRef(null);
  const closeTimerRef = useRef(null);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  const primary = useCopy();
  const reader = useCopy();

  const primaryUrl = `${window.location.origin}/s/${template.pinnedShareIds[locale]}`;
  const readerUrl = `${window.location.origin}/s/${template.shareId}`;

  useEffect(() => {
    const previous = triggerRef?.current || document.activeElement;
    // Bring the primary row under focus so a keyboard user lands on the
    // default action without tabbing through the close button first.
    primaryRowRef.current?.focus();

    const onMouseDown = (event) => {
      if (sheetRef.current?.contains(event.target)) return;
      // A click on the trigger toggles the sheet via its own onClick; let that
      // handle the event rather than double-closing here.
      if (triggerRef?.current?.contains(event.target)) return;
      onCloseRef.current();
    };
    const onKeyDown = (event) => {
      if (event.key === 'Escape') {
        onCloseRef.current();
      }
    };
    document.addEventListener('mousedown', onMouseDown);
    window.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('keydown', onKeyDown);
      if (closeTimerRef.current) clearTimeout(closeTimerRef.current);
      if (previous && typeof previous.focus === 'function') previous.focus();
    };
  }, [triggerRef]);

  const copyRow = useCallback(async (url, copy) => {
    const ok = await copy(url);
    if (!ok) return;
    if (closeTimerRef.current) clearTimeout(closeTimerRef.current);
    closeTimerRef.current = setTimeout(() => onCloseRef.current(), COPIED_DISMISS_MS);
  }, []);

  const row = ({ copied, url, copy, label, subline, rowRef }) => html`
    <button
      ref=${rowRef}
      type="button"
      className=${`btn w-100 text-start border-0 rounded d-block p-2${copied ? ' btn-success' : ''}`}
      onClick=${() => copyRow(url, copy)}
    >
      ${
        copied
          ? html`<span className="fw-semibold d-block">${t(MessageCode.SHARE_LINK_COPIED)}</span>`
          : html`<span className="fw-semibold d-block">${label}</span> <span className="text-muted d-block" style=${{ fontSize: '0.8rem' }}>${subline}</span>`
      }
    </button>
  `;

  return html`
    <div
      ref=${sheetRef}
      className="position-absolute bg-white border rounded shadow p-2"
      style=${{ top: 'calc(100% + 6px)', right: 0, minWidth: '18rem', zIndex: 1050 }}
    >
      <div className="d-flex justify-content-end">
        <button type="button" className="btn-close" aria-label=${t(MessageCode.SHARE_SHEET_DISMISS)} onClick=${onClose} />
      </div>
      ${row({
        rowRef: primaryRowRef,
        copied: primary.copied,
        url: primaryUrl,
        copy: primary.copy,
        label: t(MessageCode.SHARE_SHEET_PRIMARY),
        subline: t(MessageCode.SHARE_SHEET_PRIMARY_SUBLINE),
      })}
      ${row({
        copied: reader.copied,
        url: readerUrl,
        copy: reader.copy,
        label: t(MessageCode.SHARE_SHEET_READER_CHOICE),
        subline: t(MessageCode.SHARE_SHEET_READER_CHOICE_SUBLINE),
      })}
    </div>
  `;
}
