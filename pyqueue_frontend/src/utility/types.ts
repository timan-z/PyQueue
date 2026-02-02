// 2026-02-02-NOTE: I guess I'm sort of upgrading the minimal frontend that I built for GoQueue and SpringQueue (base) here...

/*
This Task interface now represents the *exact* API response shape exposed by the PyQueue backend.
Unlike earlier projects (GoQueue, SpringQueue base), the backend here uses enums and explicit
response schemas, so the frontend must adapt to the backend contract rather than inventing one.

Key changes compared to the older frontend model:
- Switched from `type` to `interface` to reflect a stable, backend-defined DTO rather than a
  frontend-composed structural type.
- Removed frontend-only fields (`attempts`, `maxRetries`) that are not exposed by PyQueue’s API.
- Preserved backend enum values verbatim for `type` and `status` (e.g. "EMAIL", "FAILED").
- Adopted snake_case (`created_at`) to match the wire format returned by FastAPI, avoiding
  implicit casing conversions at the API boundary.

Any UI-specific transformations (labels, formatting, derived state) should be handled in
components or view models, not in this contract type.
*/
export interface Task {
  id: string;
  payload: string;
  type: string;        // backend enum value (e.g. "EMAIL")
  status: string;      // backend enum value (e.g. "FAILED")
  created_at: string;  // ISO-8601 timestamp (PyQueue-specific)
}

// OLD /src/utility/types.ts content (this is what's in SpringQueue and GoQueue):
/*
export type Task = {
    id: string;
    payload: string;
    type: string;
    status: string;
    attempts: number;
    maxRetries: number;
    createdAt: string;
}*/
