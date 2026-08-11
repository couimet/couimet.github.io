import { StepIndicator } from '../src/components/StepIndicator.js';
import { LocaleContext } from '../src/i18n/supportedLocales.js';

import { cleanup, render, screen } from '@testing-library/react';
import htm from 'htm';
import { createElement, useState } from 'react';
import { afterEach, describe, expect, it } from 'vitest';

const html = htm.bind(createElement);

// Provides the LocaleContext that StepIndicator consumes via useLocale(),
// so tests can exercise non-default locales.
const TestWrapper = ({ children, locale = 'en' }) => {
  const [loc, setLoc] = useState(locale);
  return html`<${LocaleContext.Provider} value=${{ locale: loc, setLocale: setLoc }}>${children}</${LocaleContext.Provider}>`;
};

describe('StepIndicator', () => {
  afterEach(() => {
    cleanup();
  });

  it('renders both step labels', () => {
    render(html`<${TestWrapper}><${StepIndicator} currentStep=${0} /></${TestWrapper}>`);
    expect(screen.getByText('Choose template')).toBeTruthy();
    expect(screen.getByText('Fill in & copy')).toBeTruthy();
    expect(screen.getByText('1')).toBeTruthy();
    expect(screen.getByText('2')).toBeTruthy();
  });

  it('highlights only the first step when currentStep is 0', () => {
    render(html`<${TestWrapper}><${StepIndicator} currentStep=${0} /></${TestWrapper}>`);
    expect(screen.getByText('Choose template').className).toBe('fw-semibold');
    expect(screen.getByText('Fill in & copy').className).toBe('text-muted');
    // Circle for the active step is filled with the primary color.
    expect(screen.getByText('1').style.backgroundColor).toContain('0d6efd');
    expect(screen.getByText('2').style.backgroundColor).toBe('rgb(222, 226, 230)');
  });

  it('highlights both steps when currentStep is 1', () => {
    render(html`<${TestWrapper}><${StepIndicator} currentStep=${1} /></${TestWrapper}>`);
    expect(screen.getByText('Choose template').className).toBe('fw-semibold');
    expect(screen.getByText('Fill in & copy').className).toBe('fw-semibold');
    expect(screen.getByText('2').style.backgroundColor).toContain('0d6efd');
  });

  it('renders French labels when locale is fr', () => {
    render(html`<${TestWrapper} locale="fr"><${StepIndicator} currentStep=${0} /></${TestWrapper}>`);
    expect(screen.getByText('Choisir un modèle')).toBeTruthy();
    expect(screen.getByText('Remplir et copier')).toBeTruthy();
  });
});
