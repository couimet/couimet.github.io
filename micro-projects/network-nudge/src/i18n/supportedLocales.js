// Locale registry + stateful locale manager for the Network Nudge app.
// Plain JS, so the LocaleCode "type" is documented via JSDoc instead of TypeScript.

import { messagesEn } from './messages.en.js';
import { messagesFr } from './messages.fr.js';

import { createContext, useContext } from 'react';

/**
 * Supported locale codes for the Network Nudge app.
 * @typedef {'en' | 'fr'} LocaleCode
 */

// Locale registry: every supported locale code mapped to its message bundle.
export const supportedLocales = { en: messagesEn, fr: messagesFr };

export const DEFAULT_LOCALE = 'en';

// localStorage key persisting the user's chosen locale.
const STORAGE_KEY = 'network-nudge-locale';

// Module-scoped current locale; initialized to the default, callers can
// re-detect and apply a persisted/preferred locale on app start.
let currentLocale = DEFAULT_LOCALE;

function isSupported(locale) {
  return Object.hasOwn(supportedLocales, locale);
}

function readStoredLocale() {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function writeStoredLocale(locale) {
  try {
    localStorage.setItem(STORAGE_KEY, locale);
  } catch {
    // localStorage can be unavailable (private browsing, SSR); persistence is best-effort.
  }
}

/**
 * Resolves the active locale: stored preference, then browser language base, then default.
 * @returns {LocaleCode}
 */
export function detectLocale() {
  const stored = readStoredLocale();
  if (isSupported(stored)) return stored;

  const browserBase = typeof navigator !== 'undefined' ? String(navigator.language || '').split('-')[0] : '';
  if (isSupported(browserBase)) return browserBase;

  return DEFAULT_LOCALE;
}

/**
 * Sets the active locale, persisting it. Unsupported locales fall back to the default.
 * @param {LocaleCode} locale
 */
export function setLocale(locale) {
  currentLocale = isSupported(locale) ? locale : DEFAULT_LOCALE;
  writeStoredLocale(currentLocale);
}

/** @returns {object} message bundle for the active locale */
export function getMessages() {
  return supportedLocales[currentLocale] || supportedLocales[DEFAULT_LOCALE];
}

/** @returns {LocaleCode} active locale */
export function getCurrentLocale() {
  return currentLocale;
}

/**
 * Replaces every {key} token in message with params[key] (missing values become '').
 * @param {string} message
 * @param {Record<string, unknown>} params
 * @returns {string}
 */
export function format(message, params) {
  return message.replace(/\{([^}]+)\}/g, (_, key) => String(params?.[key] ?? ''));
}

// Context consumed by useLocale; the provider supplies { locale, setLocale }.
export const LocaleContext = createContext(null);

/**
 * React hook exposing the active locale, a locale setter, and a plain t() lookup.
 * Falls back to the module-level manager when no LocaleContext provider is mounted.
 * @returns {{ locale: LocaleCode, setLocale: (locale: LocaleCode) => void, t: (key: string) => string }}
 */
export function useLocale() {
  const context = useContext(LocaleContext);
  return {
    locale: context ? context.locale : getCurrentLocale(),
    setLocale: context ? context.setLocale : setLocale,
    // Simple key lookup, no params; parameterized messages use format(getMessages()[key], params) directly.
    // When a LocaleContext provider is mounted, resolve from its locale so the
    // provider drives translations (as in tests); otherwise fall back to the module manager.
    t: (key) => format((context ? supportedLocales[context.locale] : getMessages())[key] || key, {}),
  };
}
