The frontend treats the PyQueue backend as the authoritative source of truth.
All API-facing types and request payloads are shaped to exactly match the backend
contract, including enum values, field names, and casing.

This file intentionally performs minimal translation at the boundary (e.g., mapping
UI-friendly task type labels to backend enum values) while avoiding any reinterpretation
of backend responses. Domain concerns such as task state, retries, and timestamps are
owned entirely by the backend; the frontend adapts to these decisions rather than
influencing them.

This mirrors production backend practices (e.g., Spring DTOs and REST contracts) and
keeps the core system free to evolve independently of UI concerns.
