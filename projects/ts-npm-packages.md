---
layout: project
type: project
title: "ts-npm-packages"
date: 2026-06-10
priority: 4
published: true
repourl: https://github.com/couimet/ts-npm-packages
labels:
  - typescript
  - npm
  - monorepo
  - open-source
summary: "A curated monorepo of small TypeScript packages published under the @couimet scope on npm."
showBuyMeACoffee: true
---

A monorepo for a curated family of small TypeScript packages published under the [`@couimet`](https://www.npmjs.com/~couimet) scope on npm. These packages grew out of a desire to share code between [RangeLink](/projects/rangelink-extension.html) and [Rabbit Maximizer](/projects/rabbit-maximizer.html) without copy-pasting between repos.

## Packages

- **`@couimet/detailed-error`** — Structured error base class with typed error codes and shared error codes.
- **`@couimet/detailed-result`** — Functional `Result` type for explicit error handling, paired with `@couimet/detailed-error`.
- **`@couimet/dynamic-testing`** — Dynamic testing utilities with seeded randomness for TypeScript tests.
- **`@couimet/eslint-config`** — Shared ESLint (flat config) and Prettier configuration, usable by any TypeScript project.
- **`@couimet/eslint-plugin-barrel-imports`** — ESLint plugin with rules enforcing barrel import hygiene.
- **`@couimet/logger-contract`** — Logger interface contract; libraries depend on this without committing consumers to any logging framework.
- **`@couimet/logger-contract-adapters`** — Logger adapters that bridge `@couimet/logger-contract` with popular logging libraries.

Testing companions are also available (`@couimet/detailed-error-testing`, `@couimet/detailed-result-testing`, `@couimet/logger-contract-testing`).

The [repo](https://github.com/couimet/ts-npm-packages) is actively evolving — visit it for the latest modules that may not have made this list yet.
