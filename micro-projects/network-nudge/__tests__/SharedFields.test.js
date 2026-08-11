import { SharedFields } from '../src/components/SharedFields.js';
import { LocaleContext } from '../src/i18n/supportedLocales.js';

import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import htm from 'htm';
import { createElement, useState } from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';

const html = htm.bind(createElement);

// Provides the LocaleContext that SharedFields consumes via useLocale(),
// so tests can exercise non-default locales.
const TestWrapper = ({ children, locale = 'en' }) => {
  const [loc, setLoc] = useState(locale);
  return html`<${LocaleContext.Provider} value=${{ locale: loc, setLocale: setLoc }}>${children}</${LocaleContext.Provider}>`;
};

describe('SharedFields', () => {
  afterEach(() => {
    cleanup();
  });

  it('renders a field for each shared field definition', () => {
    const onChange = vi.fn();
    render(html`<${TestWrapper}><${SharedFields} fieldValues=${{}} onChange=${onChange} /></${TestWrapper}>`);
    expect(screen.getByLabelText('Recipient name')).toBeTruthy();
    expect(screen.getByLabelText('Role URL')).toBeTruthy();
    expect(screen.getByLabelText('Resume URL')).toBeTruthy();
  });

  it('renders the career URL label with a code-styled ChangeLog segment', () => {
    const onChange = vi.fn();
    const { container } = render(html`<${TestWrapper}><${SharedFields} fieldValues=${{}} onChange=${onChange} /></${TestWrapper}>`);
    const codeEl = container.querySelector('label code');
    expect(codeEl).toBeTruthy();
    expect(codeEl.textContent).toBe('ChangeLog');
    expect(screen.getByLabelText('Career ChangeLog URL')).toBeTruthy();
  });

  it('pre-fills field values from props', () => {
    const onChange = vi.fn();
    const fieldValues = {
      recipientName: 'Alice',
      roleUrl: 'https://example.com/job',
      careerUrl: 'https://my-career.example.com',
      resumeUrl: 'https://my-resume.example.com',
    };
    render(html`<${TestWrapper}><${SharedFields} fieldValues=${fieldValues} onChange=${onChange} /></${TestWrapper}>`);
    expect(screen.getByLabelText('Recipient name').getAttribute('value')).toBe('Alice');
    expect(screen.getByLabelText('Role URL').getAttribute('value')).toBe('https://example.com/job');
    expect(screen.getByLabelText('Career ChangeLog URL').getAttribute('value')).toBe('https://my-career.example.com');
    expect(screen.getByLabelText('Resume URL').getAttribute('value')).toBe('https://my-resume.example.com');
  });

  it('calls onChange with the field name and value when typing', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();

    // Controlled harness: mirrors App's setField, which updates fieldValues
    // from onChange so the inputs actually accumulate typed characters.
    const StatefulWrapper = () => {
      const [values, setValues] = useState({});
      return html`<${TestWrapper}><${SharedFields} fieldValues=${values} onChange=${(field, value) => {
        onChange(field, value);
        setValues((prev) => ({ ...prev, [field]: value }));
      }} /></${TestWrapper}>`;
    };

    render(html`<${StatefulWrapper} />`);
    await user.type(screen.getByLabelText('Resume URL'), 'https://r.example');
    expect(onChange).toHaveBeenCalledWith('resumeUrl', 'https://r.example');
    expect(screen.getByLabelText('Resume URL').getAttribute('value')).toBe('https://r.example');

    await user.type(screen.getByLabelText('Recipient name'), 'Bob');
    expect(onChange).toHaveBeenCalledWith('recipientName', 'Bob');
    expect(screen.getByLabelText('Recipient name').getAttribute('value')).toBe('Bob');
  });

  it('renders French labels when locale is fr', () => {
    const onChange = vi.fn();
    render(html`<${TestWrapper} locale="fr"><${SharedFields} fieldValues=${{}} onChange=${onChange} /></${TestWrapper}>`);
    expect(screen.getByLabelText('Nom du destinataire')).toBeTruthy();
    expect(screen.getByLabelText('URL du poste')).toBeTruthy();
    expect(screen.getByLabelText('URL du ChangeLog de carrière')).toBeTruthy();
    expect(screen.getByLabelText('URL du CV')).toBeTruthy();
  });
});
