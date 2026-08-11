import { TemplateCards } from '../src/components/TemplateCards.js';
import { TEMPLATES } from '../src/templates.js';

import { TestWrapper } from './helpers/localeWrapper.js';

import { cleanup, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import htm from 'htm';
import { createElement } from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';

const html = htm.bind(createElement);

describe('TemplateCards', () => {
  afterEach(() => {
    cleanup();
  });

  it('renders a card for each template', () => {
    render(html`<${TestWrapper}><${TemplateCards} templates=${TEMPLATES} sharedFieldValues=${{}} onSelect=${vi.fn()} /></${TestWrapper}>`);
    expect(screen.getByText('Direct cold application')).toBeTruthy();
    expect(screen.getByText('Cold reach-out with company')).toBeTruthy();
    expect(screen.getByText('Mutual intro request')).toBeTruthy();
    expect(screen.getAllByRole('button', { name: 'Select' })).toHaveLength(3);
  });

  it('calls onSelect with the template id when a card is selected', async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(html`<${TestWrapper}><${TemplateCards} templates=${TEMPLATES} sharedFieldValues=${{}} onSelect=${onSelect} /></${TestWrapper}>`);

    const coldCard = screen.getByText('Cold reach-out with company').closest('.card');
    await user.click(within(coldCard).getByRole('button', { name: 'Select' }));
    expect(onSelect).toHaveBeenCalledWith('cold-reachout');

    const introCard = screen.getByText('Mutual intro request').closest('.card');
    await user.click(within(introCard).getByRole('button', { name: 'Select' }));
    expect(onSelect).toHaveBeenCalledWith('mutual-intro');
  });
});
