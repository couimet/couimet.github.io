import { LocaleContext } from '../../src/i18n/supportedLocales.js';

import htm from 'htm';
import { createElement, useState } from 'react';

const html = htm.bind(createElement);

/**
 * Provides the LocaleContext that components consume via useLocale(),
 * so tests can exercise non-default locales.
 */
export const TestWrapper = ({ children, locale = 'en' }) => {
  const [loc, setLoc] = useState(locale);
  return html`<${LocaleContext.Provider} value=${{ locale: loc, setLocale: setLoc }}>${children}</${LocaleContext.Provider}>`;
};
