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
