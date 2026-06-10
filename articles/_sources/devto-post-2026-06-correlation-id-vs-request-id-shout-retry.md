# Chef retries LineCook sequence diagram

Mermaid source for the Chef retrying LineCook sequence diagram. Rendered to `articles/_sources/devto-post-2026-06-correlation-id-vs-request-id-shout-retry.png`.

<!-- Render: mmdc -i articles/_sources/devto-post-2026-06-correlation-id-vs-request-id-shout-retry.md -o articles/_sources/devto-post-2026-06-correlation-id-vs-request-id-shout-retry.png -b transparent -->

```mermaid
sequenceDiagram
    participant Chef
    participant LineCook

    Chef->>LineCook: Fire table 4, two salmon!<br/>ticket: ticket-4<br/>shout: shout-1
    LineCook-->>Chef: (silence)

    Chef->>LineCook: Fire table 4, two salmon! (2nd call)<br/>ticket: ticket-4<br/>shout: shout-2
    LineCook-->>Chef: (silence)

    Chef->>LineCook: Fire table 4, two salmon! (3rd call)<br/>ticket: ticket-4<br/>shout: shout-3
    LineCook-->>Chef: Heard!
```
