# Kitchen brigade full sequence diagram

Mermaid source for the full kitchen brigade sequence diagram. Rendered to `articles/_sources/devto-post-2026-06-correlation-id-vs-request-id-full-sequence.png`.

<!-- Render: mmdc -i articles/_sources/devto-post-2026-06-correlation-id-vs-request-id-full-sequence.md -o articles/_sources/devto-post-2026-06-correlation-id-vs-request-id-full-sequence.png -b transparent -->

```mermaid
sequenceDiagram
    participant Chef
    participant SousChef
    participant LineCook
    participant PrepCook
    participant DishWasher

    Note over Chef: Receives ticket<br/>ticket-4

    par
        Chef->>+SousChef: Prep status?<br/>ticket: ticket-4<br/>shout: shout-1
        SousChef->>+PrepCook: Mise en place?<br/>ticket: ticket-4<br/>shout: shout-3
        PrepCook-->>-SousChef: ready
        SousChef->>+DishWasher: Clean plates?<br/>ticket: ticket-4<br/>shout: shout-4
        DishWasher-->>-SousChef: ready
        SousChef-->>-Chef: ready
    and
        Chef->>+LineCook: Fire table 4, two salmon!<br/>ticket: ticket-4<br/>shout: shout-2
        LineCook-->>-Chef: (silence)
    end

    Chef->>+LineCook: Fire table 4, two salmon! (2nd call)<br/>ticket: ticket-4<br/>shout: shout-5
    LineCook-->>-Chef: (silence)

    Chef->>+LineCook: Fire table 4, two salmon! (3rd call)<br/>ticket: ticket-4<br/>shout: shout-6
    LineCook-->>-Chef: Heard!
```
