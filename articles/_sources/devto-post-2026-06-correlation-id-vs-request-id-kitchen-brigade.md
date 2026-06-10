# Kitchen brigade hierarchy diagram

Mermaid source for the kitchen brigade hierarchy flowchart. Rendered to `articles/_sources/devto-post-2026-06-correlation-id-vs-request-id-kitchen-brigade.png`.

<!-- Render: mmdc -i articles/_sources/devto-post-2026-06-correlation-id-vs-request-id-kitchen-brigade.md -o articles/_sources/devto-post-2026-06-correlation-id-vs-request-id-kitchen-brigade.png -b transparent -->

```mermaid
flowchart TD
    Chef --> SousChef
    Chef --> LineCook
    SousChef --> PrepCook
    SousChef --> DishWasher
```
