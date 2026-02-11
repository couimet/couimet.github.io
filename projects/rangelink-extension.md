---
layout: project
type: project
title: "RangeLink Extension"
date: 2025-11-09
published: true
repourl: https://github.com/couimet/rangeLink/tree/main/packages/rangelink-vscode-extension#readme
iconurl: https://raw.githubusercontent.com/couimet/rangeLink/3300130bc7d5cd9081285c06140015ac09ef0d1b/assets/icon.png
logourl: https://raw.githubusercontent.com/couimet/rangeLink/3300130bc7d5cd9081285c06140015ac09ef0d1b/assets/icon_256.png
labels:
  - vscode
  - cursor
  - ai-tools
  - extension
  - productivity
summary: "One keybinding to share precise, clickable code ranges with any AI or tool."
---

RangeLink gives you a single muscle memory for AI-assisted development: select code, hit your RangeLink shortcut, and get a GitHub-style link with character-level ranges that works in PRs, chats, terminals, and docs. It removes copy/paste friction and shortcut-juggling between Claude, Cursor, GPT, and other tools by piping links straight into your bound destinations, so your AI always sees exactly the slice of code you mean.

<h2 class="h5 mt-4 mb-2">Install</h2>

- **VS Code Marketplace**: [`couimet.rangelink-vscode-extension`](https://marketplace.visualstudio.com/items?itemName=couimet.rangelink-vscode-extension)
- **Open VSX Registry**: [`couimet/rangelink-vscode-extension`](https://open-vsx.org/extension/couimet/rangelink-vscode-extension)

<h2 class="h5 mt-4 mb-2">Core library</h2>

The RangeLink Extension is a thin wrapper around a shared TypeScript library,
`rangelink-core-ts`, which contains the parsing and link-generation logic. If you
want to integrate RangeLink-style links into other tools or editors, this is the
place to start:

- **GitHub**: [`rangelink-core-ts`](https://github.com/couimet/rangeLink/tree/main/packages/rangelink-core-ts#readme)
