---
layout: project
type: project
title: "Rabbit Maximizer"
date: 2026-06-17
priority: 2
published: true
repourl: https://github.com/couimet/rabbit-maximizer
iconurl: https://raw.githubusercontent.com/couimet/rabbit-maximizer/45827f267c558c9f689da469fce590977e903429/assets/icon.png
logourl: https://raw.githubusercontent.com/couimet/rabbit-maximizer/45827f267c558c9f689da469fce590977e903429/assets/icon_256.png
sourceiconurl: https://raw.githubusercontent.com/couimet/rabbit-maximizer/45827f267c558c9f689da469fce590977e903429/assets/icon_large.png
labels:
  - coderabbit
  - automation
  - typescript
  - dev-tools
summary: "Automates CodeRabbit's free-tier review limits so you don't have to watch the clock."
bannertitle: Rabbit Maximizer
bannersubtitle: CodeRabbit Review Automation
bannertagline: Your CodeRabbit free tier, fully squeezed.
showBuyMeACoffee: true
og_image: /img/social-banner-rabbit-maximizer.jpg
---

CodeRabbit's free tier limits how often it reviews PRs. When the limit is hit, CodeRabbit posts a review-limit comment with a wait time. Rabbit Maximizer finds these comments, waits out the cooldown, and automatically re-requests the review — so your free tier gets fully squeezed without you watching the clock.

TypeScript, Node, pnpm, Prisma (SQLite), Octokit. Runs locally as a long-lived process with a web dashboard.
