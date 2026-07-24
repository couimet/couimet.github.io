import { MessageForm } from '../src/components/MessageForm.js';
import { TEMPLATES } from '../src/templates.js';

import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import htm from 'htm';
import { createElement } from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';

const html = htm.bind(createElement);

describe('MessageForm', () => {
  const template = TEMPLATES[0]; // direct-application: 2 fields

  afterEach(() => {
    cleanup();
  });

  it('renders a field for each field definition', () => {
    const onChange = vi.fn();
    render(html`<${MessageForm} template=${template} fieldValues=${{}} onChange=${onChange} />`);
    expect(screen.getByLabelText('Recipient name')).toBeTruthy();
    expect(screen.getByLabelText('Role URL')).toBeTruthy();
  });

  it('calls onChange when a field value changes', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(html`<${MessageForm} template=${template} fieldValues=${{}} onChange=${onChange} />`);
    const input = screen.getByLabelText('Recipient name');
    await user.clear(input);
    await user.type(input, 'Test Name');
    expect(onChange).toHaveBeenCalled();
  });

  it('renders radio buttons for pronoun field in mutual-intro template', () => {
    const mutualTemplate = TEMPLATES.find((t) => t.id === 'mutual-intro');
    const onChange = vi.fn();
    render(html`<${MessageForm} template=${mutualTemplate} fieldValues=${{ pronoun: 'him' }} onChange=${onChange} />`);
    expect(screen.getByLabelText('him')).toBeTruthy();
    expect(screen.getByLabelText('her')).toBeTruthy();
    expect(screen.getByLabelText('them')).toBeTruthy();
  });

  it('pre-fills field values from props', () => {
    const onChange = vi.fn();
    render(html`<${MessageForm} template=${template} fieldValues=${{ recipientName: 'Pre-filled' }} onChange=${onChange} />`);
    const input = screen.getByLabelText('Recipient name');
    expect(input.getAttribute('value')).toBe('Pre-filled');
  });
});
