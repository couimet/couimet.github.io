import { ShareSheet } from '../src/components/ShareSheet.js';
import { TEMPLATES } from '../src/templates.js';

import { TestWrapper } from './helpers/localeWrapper.js';

import { act, cleanup, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import htm from 'htm';
import { createElement } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const html = htm.bind(createElement);

describe('ShareSheet', () => {
  const template = TEMPLATES[0]; // direct-application: plain shareId YK, pinned en Fu / fr oG

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  function stubClipboard(writeText) {
    const fn = writeText || vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal('navigator', { clipboard: { writeText: fn } });
    return fn;
  }

  function renderSheet({ locale = 'en', onClose } = {}) {
    const close = onClose || vi.fn();
    render(html`<${TestWrapper} locale=${locale}><${ShareSheet} template=${template} onClose=${close} /></${TestWrapper}>`);
    return close;
  }

  it('shows the two reader-named rows', () => {
    renderSheet();
    expect(screen.getByText("English, as you're using it")).toBeTruthy();
    expect(screen.getByText('Opens ready to fill in, in English.')).toBeTruthy();
    expect(screen.getByText('Let the reader choose')).toBeTruthy();
    expect(screen.getByText("Opens in the reader's own language, English or French.")).toBeTruthy();
  });

  it('copies the locale-pinned link from the primary row in English', async () => {
    const user = userEvent.setup();
    const writeText = stubClipboard();
    renderSheet();
    await user.click(screen.getByText("English, as you're using it"));
    expect(writeText).toHaveBeenCalledWith(expect.stringContaining('/s/Fu'));
    // The row flips to the transient copied state.
    expect(screen.getByText('Link copied!')).toBeTruthy();
    expect(screen.queryByText("English, as you're using it")).toBeNull();
    // The reader row is untouched.
    expect(screen.getByText('Let the reader choose')).toBeTruthy();
  });

  it('copies the plain template link from the reader-choice row', async () => {
    const user = userEvent.setup();
    const writeText = stubClipboard();
    renderSheet();
    await user.click(screen.getByText('Let the reader choose'));
    expect(writeText).toHaveBeenCalledWith(expect.stringContaining('/s/YK'));
    expect(screen.getByText('Link copied!')).toBeTruthy();
    expect(screen.getByText("English, as you're using it")).toBeTruthy();
  });

  it('pins the primary row to the French share link in the fr locale', async () => {
    const user = userEvent.setup();
    const writeText = stubClipboard();
    renderSheet({ locale: 'fr' });
    expect(screen.getByText("Français, tel que vous l'utilisez")).toBeTruthy();
    await user.click(screen.getByText(/Français/));
    expect(writeText).toHaveBeenCalledWith(expect.stringContaining('/s/oG'));
    expect(screen.getByText('Lien copié !')).toBeTruthy();
  });

  it('still hands out the plain template link in the reader row in French', async () => {
    const user = userEvent.setup();
    const writeText = stubClipboard();
    renderSheet({ locale: 'fr' });
    await user.click(screen.getByText('Laisser le lecteur choisir'));
    expect(writeText).toHaveBeenCalledWith(expect.stringContaining('/s/YK'));
  });

  it('closes on Escape', () => {
    const onClose = renderSheet();
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('closes on a mousedown outside the sheet', () => {
    const onClose = renderSheet();
    fireEvent.mouseDown(document.body);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('stays open on a mousedown inside the sheet', () => {
    const onClose = renderSheet();
    fireEvent.mouseDown(screen.getByText('Let the reader choose'));
    expect(onClose).not.toHaveBeenCalled();
  });

  it('stays open without copied feedback when the clipboard is unavailable', async () => {
    const user = userEvent.setup();
    stubClipboard(vi.fn().mockRejectedValue(new Error('denied')));
    const onClose = renderSheet();
    await user.click(screen.getByText("English, as you're using it"));
    expect(onClose).not.toHaveBeenCalled();
    expect(screen.queryByText('Link copied!')).toBeNull();
    expect(screen.getByText("English, as you're using it")).toBeTruthy();
  });

  it('auto-dismisses shortly after a successful copy', async () => {
    vi.useFakeTimers();
    stubClipboard();
    const onClose = renderSheet();
    fireEvent.click(screen.getByText('Let the reader choose'));
    // Flush the clipboard promise's microtasks so the copied state lands and
    // the dismiss timer is scheduled, all inside act.
    await act(async () => {});
    expect(onClose).not.toHaveBeenCalled();
    expect(screen.getByText('Link copied!')).toBeTruthy();
    act(() => {
      vi.advanceTimersByTime(1500);
    });
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
