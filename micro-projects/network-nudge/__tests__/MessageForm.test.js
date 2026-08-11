import { MessageForm } from '../src/components/MessageForm.js';
import { LocaleContext } from '../src/i18n/supportedLocales.js';
import { TEMPLATES } from '../src/templates.js';

import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import htm from 'htm';
import { createElement, useState } from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';

const html = htm.bind(createElement);

// Provides the LocaleContext that MessageForm consumes via useLocale(),
// so tests can exercise non-default locales.
const TestWrapper = ({ children, locale = 'en' }) => {
  const [loc, setLoc] = useState(locale);
  return html`<${LocaleContext.Provider} value=${{ locale: loc, setLocale: setLoc }}>${children}</${LocaleContext.Provider}>`;
};

describe('MessageForm', () => {
  const template = TEMPLATES[0]; // direct-application: 2 fields

  afterEach(() => {
    cleanup();
  });

  it('renders a field for each field definition', () => {
    const onChange = vi.fn();
    render(html`<${TestWrapper}><${MessageForm} template=${template} fieldValues=${{}} onChange=${onChange} /></${TestWrapper}>`);
    expect(screen.getByLabelText('Recipient name')).toBeTruthy();
    expect(screen.getByLabelText('Role URL')).toBeTruthy();
  });

  it('calls onChange when a field value changes', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(html`<${TestWrapper}><${MessageForm} template=${template} fieldValues=${{}} onChange=${onChange} /></${TestWrapper}>`);
    const input = screen.getByLabelText('Recipient name');
    await user.clear(input);
    await user.type(input, 'Test Name');
    expect(onChange).toHaveBeenCalled();
  });

  it('renders radio buttons for pronoun field in mutual-intro template', () => {
    const mutualTemplate = TEMPLATES.find((t) => t.id === 'mutual-intro');
    const onChange = vi.fn();
    render(html`<${TestWrapper}><${MessageForm} template=${mutualTemplate} fieldValues=${{ pronoun: 'him' }} onChange=${onChange} /></${TestWrapper}>`);
    expect(screen.getByLabelText('him')).toBeTruthy();
    expect(screen.getByLabelText('her')).toBeTruthy();
    expect(screen.getByLabelText('them')).toBeTruthy();
  });

  it('pre-fills field values from props', () => {
    const onChange = vi.fn();
    render(html`<${TestWrapper}><${MessageForm} template=${template} fieldValues=${{ recipientName: 'Pre-filled' }} onChange=${onChange} /></${TestWrapper}>`);
    const input = screen.getByLabelText('Recipient name');
    expect(input.getAttribute('value')).toBe('Pre-filled');
  });

  it('renders French labels when locale is fr', () => {
    const mutualTemplate = TEMPLATES.find((t) => t.id === 'mutual-intro');
    const onChange = vi.fn();
    render(html`<${TestWrapper} locale="fr"><${MessageForm} template=${mutualTemplate} fieldValues=${{}} onChange=${onChange} /></${TestWrapper}>`);
    expect(screen.getByLabelText('Nom du destinataire')).toBeTruthy();
    expect(screen.getByLabelText('URL du poste')).toBeTruthy();
    expect(screen.getByLabelText('lui')).toBeTruthy();
    expect(screen.getByLabelText('elle')).toBeTruthy();
    expect(screen.getByLabelText('eux')).toBeTruthy();
  });
});
