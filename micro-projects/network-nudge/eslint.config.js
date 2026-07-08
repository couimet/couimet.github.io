import baseConfig, { reactConfig } from '@couimet/eslint-config';
import reactPlugin from 'eslint-plugin-react';
import reactHooksPlugin from 'eslint-plugin-react-hooks';

export default [
  ...baseConfig,
  ...reactConfig({
    plugins: { 'react-hooks': reactHooksPlugin, react: reactPlugin },
  }),
  {
    files: ['__tests__/**/*.js'],
    rules: {
      'no-magic-numbers': 'off',
    },
  },
];
