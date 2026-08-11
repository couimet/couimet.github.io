import { TemplateCard } from '../src/components/TemplateCard.js';
import { LocaleContext } from '../src/i18n/supportedLocales.js';
import { TEMPLATES } from '../src/templates.js';

import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import htm from 'htm';
import { createElement, useState } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const html = htm.bind(createElement);

// Provides the LocaleContext that TemplateCard consumes via useLocale(),
// so tests can exercise non-default locales.
const TestWrapper = ({ children, locale = 'en' }) => {
  const [loc, setLoc] = useState(locale);
  return html`<${LocaleContext.Provider} value=${{ locale: loc, setLocale: setLoc }}>${children}</${LocaleContext.Provider}>`;
};

describe('TemplateCard', () => {
  const template = TEMPLATES[0]; // direct-application
  const completeFields = {
    recipientName: 'Alice',
    roleUrl: 'https://example.com/job',
    careerUrl: 'https://my-career.example.com',
    resumeUrl: 'https://my-resume.example.com',
  };

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it('renders the template title and description', () => {
    render(html`<${TestWrapper}><${TemplateCard} template=${template} sharedFieldValues=${{}} onSelect=${vi.fn()} /></${TestWrapper}>`);
    expect(screen.getByText('Direct cold application')).toBeTruthy();
    expect(screen.getByText('You found a role and want to reach the hiring manager or talent team directly.')).toBeTruthy();
  });

  it('shows the preview with placeholder brackets when fields are empty', () => {
    const { container } = render(html`<${TestWrapper}><${TemplateCard} template=${template} sharedFieldValues=${{}} onSelect=${vi.fn()} /></${TestWrapper}>`);
    const preview = container.querySelector('pre').textContent;
    expect(preview).toContain('[Recipient name]');
    expect(preview).toContain('[Role URL]');
    expect(preview).toContain('[Career ChangeLog URL]');
    expect(preview).toContain('[Resume URL]');
  });

  it('calls onSelect when the Select button is clicked', async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(html`<${TestWrapper}><${TemplateCard} template=${template} sharedFieldValues=${{}} onSelect=${onSelect} /></${TestWrapper}>`);
    await user.click(screen.getByText('Select'));
    expect(onSelect).toHaveBeenCalledTimes(1);
  });

  it('shows the copy button when all fields are filled', () => {
    render(html`<${TestWrapper}><${TemplateCard} template=${template} sharedFieldValues=${completeFields} onSelect=${vi.fn()} /></${TestWrapper}>`);
    expect(screen.getByTitle('Copy to clipboard')).toBeTruthy();
  });

  it('hides the copy button when fields are incomplete', () => {
    render(html`<${TestWrapper}><${TemplateCard} template=${template} sharedFieldValues=${{}} onSelect=${vi.fn()} /></${TestWrapper}>`);
    expect(screen.queryByTitle('Copy to clipboard')).toBeNull();
  });

  it('copies the preview to the clipboard and shows feedback', async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal('navigator', { clipboard: { writeText } });

    const { container } = render(
      html`<${TestWrapper}><${TemplateCard} template=${template} sharedFieldValues=${completeFields} onSelect=${onSelect} /></${TestWrapper}>`,
    );
    const preview = container.querySelector('pre').textContent;
    await user.click(screen.getByTitle('Copy to clipboard'));
    expect(writeText).toHaveBeenCalledWith(preview);
    expect(await screen.findByText('Copied!')).toBeTruthy();
    // Copy must not trigger template selection.
    expect(onSelect).not.toHaveBeenCalled();
  });

  it('does not show copy feedback when the clipboard is unavailable', async () => {
    const user = userEvent.setup();
    vi.stubGlobal('navigator', { clipboard: { writeText: vi.fn().mockRejectedValue(new Error('denied')) } });

    render(html`<${TestWrapper}><${TemplateCard} template=${template} sharedFieldValues=${completeFields} onSelect=${vi.fn()} /></${TestWrapper}>`);
    await user.click(screen.getByTitle('Copy to clipboard'));
    expect(screen.queryByText('Copied!')).toBeNull();
  });

  it('renders French title and description when locale is fr', () => {
    render(html`<${TestWrapper} locale="fr"><${TemplateCard} template=${template} sharedFieldValues=${{}} onSelect=${vi.fn()} /></${TestWrapper}>`);
    expect(screen.getByText('Candidature directe')).toBeTruthy();
    expect(screen.getByText(/Vous avez trouvé un poste et souhaitez contacter directement/)).toBeTruthy();
  });

  it('clears the previous copy timeout on rapid double-click', async () => {
    const user = userEvent.setup();
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal('navigator', { clipboard: { writeText } });

    render(html`<${TestWrapper}><${TemplateCard} template=${template} sharedFieldValues=${completeFields} onSelect=${vi.fn()} /><//>`);
    const copyBtn = screen.getByRole('button', { name: 'Copy to clipboard' });
    await user.click(copyBtn);
    await user.click(copyBtn);
    expect(writeText).toHaveBeenCalledTimes(2);
  });
});
