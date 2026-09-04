---
layout: project
type: project
title: "Network Nudge"
date: 2026-07-07
priority: 5
iconurl: /micro-projects/network-nudge/assets/icon.png
logourl: /micro-projects/network-nudge/assets/icon_256.png
sourceiconurl: /micro-projects/network-nudge/assets/icon_large.png
labels:
  - outreach
  - linkedin
  - react
  - career
summary: "Build personalized LinkedIn outreach messages from templates. Pick a type, fill in the blanks, copy — no more placeholder slip-ups."
bannertitle: Network Nudge
bannersubtitle: Outreach Message Builder
bannertagline: Pick a template, fill in the blanks, copy — no more placeholder slip-ups.
showBuyMeACoffee: true
og_image: /img/social-banner-network-nudge.jpg
---

Network Nudge replaces the copy-pasta grind of outreach messages. Pick a template, fill in the shared fields, and copy — the message preview updates live as you type.

<!-- Inert anchors matching the template ids the app reads from the hash.
     The /s/<ID> share pages deep-link here (e.g. #cold-reachout), and the
     static ids let link checks resolve those hashes against this page. The
     en--/fr-- ids back the locale-pinned compose shares (#en--<template>,
     #fr--<template>). -->
<span id="direct-application"></span><span id="cold-reachout"></span><span id="mutual-intro"></span><span id="en--direct-application"></span><span id="en--cold-reachout"></span><span id="en--mutual-intro"></span><span id="fr--direct-application"></span><span id="fr--cold-reachout"></span><span id="fr--mutual-intro"></span>

<div id="root"></div>

<script type="importmap">
{
  "imports": {
    "react": "https://esm.sh/react@19",
    "react-dom/": "https://esm.sh/react-dom@19/",
    "htm": "https://esm.sh/htm@3"
  }
}
</script>
<script type="module">
  import { createRoot } from "react-dom/client";
  import { createElement } from "react";
  import htm from "htm";
  import { App } from "/micro-projects/network-nudge/src/components/App.js";

  const html = htm.bind(createElement);
  createRoot(document.getElementById("root")).render(
    html`<${App}
      careerUrlDefault="https://ouimet.info/#career-changelog"
      resumeUrlDefault="https://ouimet.info/charles/resume/latest"
    />`
  );
</script>
