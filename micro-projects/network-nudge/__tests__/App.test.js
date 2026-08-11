import { App } from '../src/components/App.js';

import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import htm from 'htm';
import { createElement } from 'react';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

const html = htm.bind(createElement);

describe('App', () => {
  beforeEach(() => {
    localStorage.clear();
    window.location.hash = '';
  });

  afterEach(() => {
    cleanup();
    localStorage.clear();
    window.location.hash = '';
  });

  it('renders the EN/FR toggle buttons and the template list by default', () => {
    render(html`<${App} />`);
    expect(screen.getByRole('button', { name: 'EN' })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'FR' })).toBeTruthy();
    expect(screen.getByText('Choose template')).toBeTruthy();
    expect(screen.getAllByRole('button', { name: 'Select' })).toHaveLength(3);
  });

  it('switches child components to French when FR is clicked and back with EN', async () => {
    const user = userEvent.setup();
    render(html`<${App} />`);
    expect(screen.getByText('Choose template')).toBeTruthy();

    await user.click(screen.getByRole('button', { name: 'FR' }));
    expect(window.location.hash).toBe('#fr');
    expect(screen.getByText('Choisir un modèle')).toBeTruthy();
    expect(screen.getByText('Remplir et copier')).toBeTruthy();
    expect(screen.getByLabelText('URL du CV')).toBeTruthy();
    expect(screen.getByText('Candidature directe')).toBeTruthy();
    expect(screen.queryByText('Choose template')).toBeNull();

    await user.click(screen.getByRole('button', { name: 'EN' }));
    expect(screen.getByText('Choose template')).toBeTruthy();
    expect(screen.getByLabelText('Resume URL')).toBeTruthy();
  });

  it('restores the selected template from the URL hash on mount', () => {
    window.location.hash = '#mutual-intro';
    render(html`<${App} />`);
    expect(screen.getByText('← Back to templates')).toBeTruthy();
    expect(screen.queryAllByRole('button', { name: 'Select' })).toHaveLength(0);
    // Step 2 shows the message form for the restored template.
    expect(screen.getByLabelText('Recipient name')).toBeTruthy();
    expect(screen.getByText('Mutual intro request')).toBeTruthy();
  });

  it('ignores an unknown hash on mount', () => {
    window.location.hash = '#does-not-exist';
    render(html`<${App} />`);
    expect(screen.getAllByRole('button', { name: 'Select' })).toHaveLength(3);
  });

  it('selects a template, sets the hash, and fills in shared fields from step 1', async () => {
    const user = userEvent.setup();
    render(html`<${App} />`);
    await user.click(screen.getAllByRole('button', { name: 'Select' })[0]);
    expect(screen.getByText('← Back to templates')).toBeTruthy();
    expect(window.location.hash).toContain('direct-application');
  });

  it('localizes the back button text', async () => {
    const user = userEvent.setup();
    window.location.hash = '#mutual-intro';
    render(html`<${App} />`);
    expect(screen.getByText('← Back to templates')).toBeTruthy();

    // Go back, switch to French, and re-select a template.
    await user.click(screen.getByText('← Back to templates'));
    await user.click(screen.getByRole('button', { name: 'FR' }));
    await user.click(screen.getAllByRole('button', { name: 'Sélectionner' })[0]);
    expect(screen.getByText('Retour aux modèles')).toBeTruthy();
  });

  it('retains shared field values when going back to the template list', async () => {
    const user = userEvent.setup();
    render(html`<${App} />`);
    await user.type(screen.getByLabelText('Recipient name'), 'Alice');
    expect(screen.getByLabelText('Recipient name').getAttribute('value')).toBe('Alice');

    await user.click(screen.getAllByRole('button', { name: 'Select' })[0]);
    expect(screen.getByLabelText('Recipient name').getAttribute('value')).toBe('Alice');

    await user.click(screen.getByText('← Back to templates'));
    expect(screen.getByLabelText('Recipient name').getAttribute('value')).toBe('Alice');
    expect(window.location.hash).toBe('#en');
  });

  it('pre-fills shared fields from the default props', () => {
    render(html`<${App} careerUrlDefault="https://my.example.com/career" resumeUrlDefault="https://resume.example.com" />`);
    expect(screen.getByLabelText('Career ChangeLog URL').getAttribute('value')).toBe('https://my.example.com/career');
    expect(screen.getByLabelText('Resume URL').getAttribute('value')).toBe('https://resume.example.com');
  });

  it('handles a hash with locale and trailing separator (#en--)', () => {
    window.location.hash = '#en--';
    render(html`<${App} />`);
    expect(screen.getByText('Choose template')).toBeTruthy();
  });

  it('restores locale and template from a combined hash', () => {
    window.location.hash = '#fr--direct-application';
    render(html`<${App} />`);
    expect(screen.getByText('Retour aux modèles')).toBeTruthy();
    expect(screen.queryAllByRole('button', { name: 'Select' })).toHaveLength(0);
  });
});
