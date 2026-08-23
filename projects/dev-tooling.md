---
layout: project
type: project
title: "dev-tooling"
date: 2025-02-20
priority: 7
published: true
repourl: https://github.com/couimet/dev-tooling
labels:
  - macos
  - devops
  - automation
  - shell-scripts
summary: "macOS setup scripts that automate the grind of provisioning a fresh machine."
showBuyMeACoffee: true
---

`dev-tooling` is a small collection of macOS setup scripts. The idea is to automate as much of the environment as possible: hit the ground running in a new role, or get a laptop back up fast after a flash, a reinstall, or a dead drive. The setup lives in scripts you can re-run anytime.

It started in February 2025 with a single script, `setup-osx.sh`, written to provision a Mac for an upcoming role. The [CHANGELOG](https://github.com/couimet/dev-tooling/blob/main/CHANGELOG.md) tracks what has changed since. It stays small on purpose: each entry is there because I got tired of doing that step by hand.

<h2 class="h5 mt-4 mb-2">Quality</h2>

The scripts are tested with BATS and linted with shellcheck in CI on every push and PR.

The [repo README](https://github.com/couimet/dev-tooling#readme) has the full details, including a one-line install.
