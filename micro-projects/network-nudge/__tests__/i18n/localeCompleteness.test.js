import { MessageCode } from '../../src/i18n/messageCodes.js';
import {
  applyLocale,
  DEFAULT_LOCALE,
  detectLocale,
  format,
  getCurrentLocale,
  getMessages,
  LocaleContext,
  setLocale,
  supportedLocales,
  useLocale,
} from '../../src/i18n/supportedLocales.js';

import { cleanup, render, screen } from '@testing-library/react';
import htm from 'htm';
import { createElement, useState } from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';

const html = htm.bind(createElement);

/**
 * Automated validation of locale completeness.
 *
 * Ensures all locales in supportedLocales registry have:
 * 1. Messages for all MessageCode values (no missing keys)
 * 2. No extra keys beyond MessageCode enum (no orphaned translations)
 * 3. Exactly the same number of keys as MessageCode enum
 * 4. No message value that is empty or undefined
 * 5. Same {placeholder} set as English for every translatable message
 */
function extractPlaceholders(message) {
  if (typeof message !== 'string') return [];
  const matches = message.match(/\{([^}]+)\}/g) || [];
  return [...new Set(matches)].sort();
}
describe('Locale Completeness', () => {
  const allMessageCodes = Object.values(MessageCode);

  // Iterate over all supported locales
  Object.entries(supportedLocales).forEach(([locale, messages]) => {
    describe(`Locale: ${locale}`, () => {
      it('should have messages for all MessageCode values', () => {
        allMessageCodes.forEach((code) => {
          expect(messages[code]).toBeDefined();
          expect(messages[code]).not.toBe('');
        });
      });

      it('should not have extra keys beyond MessageCode enum', () => {
        const messageKeys = Object.keys(messages);
        messageKeys.forEach((key) => {
          expect(allMessageCodes).toContain(key);
        });
      });

      it('should have exactly the same number of keys as MessageCode enum', () => {
        const messageKeys = Object.keys(messages);
        expect(messageKeys).toHaveLength(allMessageCodes.length);
      });

      // Compare placeholder sets against English for every message code.
      if (locale !== DEFAULT_LOCALE) {
        it('should have the same {placeholder} set as English for every message', () => {
          const enMessages = supportedLocales[DEFAULT_LOCALE];
          allMessageCodes.forEach((code) => {
            const enPlaceholders = extractPlaceholders(enMessages[code]);
            const localePlaceholders = extractPlaceholders(messages[code]);
            expect(localePlaceholders, `${code} placeholder mismatch`).toEqual(enPlaceholders);
          });
        });
      }
    });
  });
});

describe('Locale manager', () => {
  const STORAGE_KEY = 'network-nudge-locale';

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    // setLocale persists the locale to localStorage; clear after it so no
    // stale stored locale leaks into the next test's detectLocale().
    setLocale(DEFAULT_LOCALE);
    localStorage.clear();
  });

  it('setLocale persists a supported locale', () => {
    setLocale('fr');
    expect(getCurrentLocale()).toBe('fr');
    expect(localStorage.getItem(STORAGE_KEY)).toBe('fr');
  });

  it('setLocale falls back to the default for unsupported locales', () => {
    setLocale('xx');
    expect(getCurrentLocale()).toBe(DEFAULT_LOCALE);
    expect(localStorage.getItem(STORAGE_KEY)).toBe(DEFAULT_LOCALE);
  });

  it('setLocale falls back to the default for falsy locales', () => {
    setLocale(null);
    expect(getCurrentLocale()).toBe(DEFAULT_LOCALE);
  });

  it('applyLocale applies a supported locale without persisting it', () => {
    localStorage.setItem(STORAGE_KEY, 'en');
    applyLocale('fr');
    expect(getCurrentLocale()).toBe('fr');
    expect(localStorage.getItem(STORAGE_KEY)).toBe('en');
  });

  it('applyLocale falls back to the default for unsupported locales', () => {
    applyLocale('xx');
    expect(getCurrentLocale()).toBe(DEFAULT_LOCALE);
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
  });

  it('applyLocale leaves no stored value behind when none was set', () => {
    applyLocale('fr');
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
  });

  it('detectLocale returns the stored locale when supported', () => {
    localStorage.setItem(STORAGE_KEY, 'fr');
    expect(detectLocale()).toBe('fr');
  });

  it('detectLocale falls back to the browser language when the stored locale is unsupported', () => {
    localStorage.setItem(STORAGE_KEY, 'xx');
    vi.stubGlobal('navigator', { language: 'fr-FR' });
    expect(detectLocale()).toBe('fr');
  });

  it('detectLocale returns the default when the browser language is unsupported', () => {
    vi.stubGlobal('navigator', { language: 'xx-ZZ' });
    expect(detectLocale()).toBe(DEFAULT_LOCALE);
  });

  it('detectLocale returns the default when the browser language is empty', () => {
    vi.stubGlobal('navigator', { language: '' });
    expect(detectLocale()).toBe(DEFAULT_LOCALE);
  });

  it('detectLocale returns the default when navigator is unavailable', () => {
    vi.stubGlobal('navigator', undefined);
    expect(detectLocale()).toBe(DEFAULT_LOCALE);
  });

  it('detectLocale ignores localStorage read errors', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('storage denied');
    });
    expect(detectLocale()).toBe(DEFAULT_LOCALE);
  });

  it('setLocale ignores localStorage write errors', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('quota exceeded');
    });
    expect(() => setLocale('fr')).not.toThrow();
    expect(getCurrentLocale()).toBe('fr');
  });

  it('getMessages falls back to the default bundle when the active locale is unavailable', () => {
    setLocale('fr');
    const frBundle = supportedLocales.fr;
    delete supportedLocales.fr;
    try {
      expect(getMessages()).toBe(supportedLocales[DEFAULT_LOCALE]);
    } finally {
      supportedLocales.fr = frBundle;
    }
  });

  it('format replaces tokens and treats missing params as empty strings', () => {
    expect(format('Hi {name}!', { name: 'Alice' })).toBe('Hi Alice!');
    expect(format('Hi {name}!', {})).toBe('Hi !');
    expect(format('Hi {name}!', null)).toBe('Hi !');
  });

  it('format handles empty and token-free messages', () => {
    expect(format('', {})).toBe('');
    expect(format('No tokens here', undefined)).toBe('No tokens here');
  });

  it('useLocale falls back to the module manager outside a provider', () => {
    setLocale('fr');
    function Probe() {
      const { locale, t } = useLocale();
      return html`<span>${locale}:${t('MISSING_KEY')}</span>`;
    }
    render(html`<${Probe} />`);
    expect(screen.getByText('fr:MISSING_KEY')).toBeTruthy();
  });

  it('useLocale resolves t() from the provider locale', () => {
    const TestWrapper = ({ children, locale = 'en' }) => {
      const [loc, setLoc] = useState(locale);
      return html`<${LocaleContext.Provider} value=${{ locale: loc, setLocale: setLoc }}>${children}</${LocaleContext.Provider}>`;
    };
    function Probe() {
      const { locale, t } = useLocale();
      return html`<span>${locale}:${t(MessageCode.STEP_CHOOSE_TEMPLATE)}</span>`;
    }
    render(html`<${TestWrapper} locale="fr"><${Probe} /></${TestWrapper}>`);
    expect(screen.getByText('fr:Choisir un modèle')).toBeTruthy();
  });
});
