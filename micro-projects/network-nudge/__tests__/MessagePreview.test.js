import { MessagePreview } from '../src/components/MessagePreview.js';
import { TEMPLATES } from '../src/templates.js';

import { TestWrapper } from './helpers/localeWrapper.js';

import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import htm from 'htm';
import { createElement } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const html = htm.bind(createElement);

describe('MessagePreview', () => {
  const template = TEMPLATES[0]; // direct-application
  const fieldValues = {
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

  it('renders the composed message in a textarea', () => {
    render(html`<${TestWrapper}><${MessagePreview} template=${template} fieldValues=${fieldValues} /><//>`);
    const textarea = screen.getByRole('textbox');
    expect(textarea.value).toContain('Hi Alice!');
    expect(textarea.value).toContain('https://example.com/job');
  });

  it('shows character count', () => {
    render(html`<${TestWrapper}><${MessagePreview} template=${template} fieldValues=${fieldValues} /><//>`);
    const countEls = screen.getAllByText(/characters/);
    expect(countEls.length).toBeGreaterThan(0);
    expect(countEls[0].textContent).toMatch(/\d+ \/ 300/);
  });

  it('shows over-limit warning when message exceeds 300 characters', () => {
    const longFieldValues = {
      recipientName: 'Alice',
      roleUrl: 'https://example.com/job/' + 'x'.repeat(320),
      careerUrl: 'https://my-career.example.com',
      resumeUrl: 'https://my-resume.example.com',
    };
    render(html`<${TestWrapper}><${MessagePreview} template=${template} fieldValues=${longFieldValues} /><//>`);
    expect(screen.getByText(/over LinkedIn limit/)).toBeTruthy();
  });

  it('suppresses over-limit warning when linkedinLimit is disabled', () => {
    const longTemplate = {
      ...template,
      linkedinLimit: false,
    };
    const longFieldValues = {
      recipientName: 'Alice',
      roleUrl: 'https://example.com/job/' + 'x'.repeat(320),
      careerUrl: 'https://my-career.example.com',
      resumeUrl: 'https://my-resume.example.com',
    };
    render(html`<${TestWrapper}><${MessagePreview} template=${longTemplate} fieldValues=${longFieldValues} /><//>`);
    expect(screen.queryByText(/over LinkedIn limit/)).toBeNull();
    expect(screen.getByText(/characters/).textContent).toMatch(/^\d+ characters$/);
  });

  it('shows character count without LinkedIn limit for mutual-intro', () => {
    const mutualTemplate = TEMPLATES.find((t) => t.id === 'mutual-intro');
    const fields = {
      recipientName: 'Alice',
      targetName: 'Bob',
      targetLinkedInUrl: 'https://linkedin.com/in/bob',
      companyName: 'Acme',
      roleUrl: 'https://example.com/job',
      pronoun: 'him',
    };
    render(html`<${TestWrapper}><${MessagePreview} template=${mutualTemplate} fieldValues=${fields} /><//>`);
    const el = screen.getByText(/characters/);
    expect(el.textContent).toMatch(/^\d+ characters$/);
    expect(el.className).not.toContain('text-danger');
  });

  it('shows French character count label when locale is fr', () => {
    render(html`<${TestWrapper} locale="fr"><${MessagePreview} template=${template} fieldValues=${fieldValues} /><//>`);
    expect(screen.getByText(/caractères/)).toBeTruthy();
    expect(screen.queryByText(/characters/)).toBeNull();
    const textarea = screen.getByRole('textbox');
    expect(textarea.value).toContain('Bonjour Alice');
    expect(textarea.value).toContain('Disponible pour en discuter');
  });

  it('copies message to clipboard when button is clicked', async () => {
    const user = userEvent.setup();
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal('navigator', { clipboard: { writeText } });

    render(html`<${TestWrapper}><${MessagePreview} template=${template} fieldValues=${fieldValues} /><//>`);
    await user.click(screen.getByText('Copy to clipboard'));
    expect(writeText).toHaveBeenCalledWith(expect.stringContaining('Hi Alice!'));
  });

  it('updates preview when user types in the textarea', async () => {
    const user = userEvent.setup();
    render(html`<${TestWrapper}><${MessagePreview} template=${template} fieldValues=${fieldValues} /><//>`);
    const textarea = screen.getByRole('textbox');
    await user.clear(textarea);
    await user.type(textarea, 'Custom message edited by user');
    expect(textarea.value).toBe('Custom message edited by user');
  });

  it('shows reset link after editing and resets on click', async () => {
    const user = userEvent.setup();
    render(html`<${TestWrapper}><${MessagePreview} template=${template} fieldValues=${fieldValues} /><//>`);
    const textarea = screen.getByRole('textbox');
    const originalValue = textarea.value;

    await user.clear(textarea);
    await user.type(textarea, 'Temporary edit');

    expect(textarea.value).toBe('Temporary edit');
    expect(screen.getByText('Reset to template')).toBeTruthy();

    await user.click(screen.getByText('Reset to template'));
    expect(textarea.value).toBe(originalValue);
  });

  it('resets edited text when template changes', async () => {
    const user = userEvent.setup();
    const template2 = TEMPLATES[1]; // cold-reachout
    const secondFieldValues = {
      recipientName: 'Bob',
      companyName: 'Acme Corp',
      roleUrl: 'https://example.com/job2',
      careerUrl: 'https://my-career.example.com',
      resumeUrl: 'https://my-resume.example.com',
    };

    const { rerender } = render(html`<${TestWrapper}><${MessagePreview} template=${template} fieldValues=${fieldValues} /><//>`);
    const textarea = screen.getByRole('textbox');

    // Edit the text to something custom
    await user.clear(textarea);
    await user.type(textarea, 'My custom edit that should not survive a template change');

    // Change to a different template
    rerender(html`<${TestWrapper}><${MessagePreview} template=${template2} fieldValues=${secondFieldValues} /><//>`);

    // Text should be the new template's composed message, not the edit
    expect(textarea.value).toContain('Hi Bob!');
    expect(textarea.value).toContain('Acme Corp');
    expect(textarea.value).not.toContain('My custom edit');
  });

  describe('with missing fields', () => {
    it('shows placeholder text for missing values', () => {
      render(html`<${TestWrapper}><${MessagePreview} template=${template} fieldValues=${{}} /><//>`);
      const textarea = screen.getByRole('textbox');
      expect(textarea.value).toContain('[Recipient name]');
      expect(textarea.value).toContain('[Role URL]');
      expect(textarea.value).toContain('[Career ChangeLog URL]');
      expect(textarea.value).toContain('[Resume URL]');
    });

    it('shows a warning alert listing missing field labels', () => {
      render(html`<${TestWrapper}><${MessagePreview} template=${template} fieldValues=${{}} /><//>`);
      const alert = screen.getByText(/Missing:/).closest('.alert');
      expect(alert).toBeTruthy();
      expect(alert.textContent).toContain('Recipient name');
      expect(alert.textContent).toContain('Role URL');
    });

    it('disables the copy button', () => {
      render(html`<${TestWrapper}><${MessagePreview} template=${template} fieldValues=${{}} /><//>`);
      const button = screen.getByText('Copy to clipboard');
      expect(button.disabled).toBe(true);
    });

    it('enables the copy button when all fields are filled', () => {
      render(html`<${TestWrapper}><${MessagePreview} template=${template} fieldValues=${fieldValues} /><//>`);
      const button = screen.getByText('Copy to clipboard');
      expect(button.disabled).toBe(false);
    });

    it('handles clipboard rejection without crashing', async () => {
      const user = userEvent.setup();
      const writeText = vi.fn().mockRejectedValue(new Error('denied'));
      vi.stubGlobal('navigator', { clipboard: { writeText } });

      render(html`<${TestWrapper}><${MessagePreview} template=${template} fieldValues=${fieldValues} /><//>`);
      await user.click(screen.getByText('Copy to clipboard'));
      // No crash, no "Copied!" feedback on failure.
      expect(screen.getByText('Copy to clipboard')).toBeTruthy();
      expect(screen.queryByText('Copied!')).toBeNull();
    });
  });
});
