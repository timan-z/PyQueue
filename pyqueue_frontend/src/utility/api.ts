// 2026-02-02-NOTE: I guess I'm sort of upgrading the minimal frontend that I built for GoQueue and SpringQueue (base) here...
// ********************
// src/utility/api.ts:
// This file acts as the boundary adapter between the frontend UI and the PyQueue backend API.
// The backend is treated as the source of truth; this layer exists to translate UI-friendly
// inputs into backend-valid request shapes and to expose backend responses verbatim.

const API_BASE = import.meta.env.VITE_API_BASE.replace(/\/+$/, "");

/* 2026-02-02-NOTE:
It's been a little while but I guess that in my GoQueue project and perhaps SpringQueue (base),
I wasn't yet using enums -- but I decided to go with them from the get-go with PyQueue because why not -- however,
I inevitably face this discrepancy where the frontend is still hardcoded with the original string categorizations I had.
Thus, I'll define a little mapper here to get around that.

Formally, for later documentation:
```
In earlier projects (GoQueue, SpringQueue base), task types were passed as raw strings.
PyQueue introduces backend enums for TaskType, which creates a mismatch between UI labels
and backend expectations. This mapping resolves that mismatch without weakening the backend.
```
*/
const TASK_TYPE_MAP: Record<string, string> = {
  "email": "EMAIL",
  "report": "REPORT",
  "data-cleanup": "DATACLEANUP",
  "sms": "SMS",
  "newsletter": "NEWSLETTER",
  "takes-long": "TAKESLONG",
  "fail": "FAIL",
  "fail-absolute": "FAILABS",
};

// Read Operations:
export const getAllJobs = async () => {
  const result = await fetch(`${API_BASE}/api/jobs`, {
    method: "GET",
  });

  if (!result.ok) {
    throw new Error("ERROR: Failed to return data for all jobs.");
  }

  return result.json();
};

export const getJobById = async (id: string) => {
  const result = await fetch(`${API_BASE}/api/jobs/${id}`, {
    method: "GET",
  });

  if (!result.ok) {
    throw new Error(
      `ERROR: Failed to return data for specific job (ID: ${id}).`
    );
  }

  return result.json();
};

// Write (Mutation) Operations:
export const enqueueJob = async (payload: string, uiType: string) => {
  const backendType = TASK_TYPE_MAP[uiType];

  if (!backendType) {
    throw new Error(`ERROR: Unknown task type '${uiType}'.`);
  }

  const result = await fetch(`${API_BASE}/api/enqueue`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      payload,
      t_type: backendType, // backend enum value
    }),
  });

  if (!result.ok) {
    throw new Error(
      `ERROR: Failed to enqueue new job (payload: ${payload}, type: ${backendType}).`
    );
  }

  return result.json();
};

export const deleteJob = async (id: string) => {
  const result = await fetch(`${API_BASE}/api/jobs/${id}`, {
    method: "DELETE",
  });

  if (!result.ok) {
    throw new Error(`ERROR: Failed to delete job (ID: ${id}).`);
  }

  return result.json();
};

export const retryJob = async (id: string) => {
  const result = await fetch(`${API_BASE}/api/jobs/${id}/retry`, {
    method: "POST",
  });

  if (!result.ok) {
    throw new Error(`ERROR: Failed to retry job (ID: ${id}).`);
  }

  return result.json();
};

export const clearQueue = async () => {
  const result = await fetch(`${API_BASE}/api/clear`, {
    method: "POST",
  });

  if (!result.ok) {
    throw new Error("ERROR: Failed to clear the queue.");
  }

  return result.json();
};
