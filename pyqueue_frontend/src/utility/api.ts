const API_BASE = import.meta.env.VITE_API_BASE.replace(/\/+$/, "");

export const getAllJobs = async() => {
    const result = await fetch(`${API_BASE}/api/jobs`, {
        method:"GET"
    });
    if(!result.ok) throw new Error("ERROR: Failed to return data for all jobs.");
    return await result.json();
}

export const getJobById = async(id: string) => {
    const result = await fetch(`${API_BASE}/api/jobs/${id}`, {
        method:"GET"
    });

    console.log("STATUS:", result.status);
    const text = await result.text();
    console.log("RAW:", text);

    if(!result.ok) throw new Error(`ERROR: Failed to return data for specific job (by ID:${id}).`);
    return await result.json();
}

export const enqueueJob = async(payload: string, type: string) => {
    const result = await fetch(`${API_BASE}/api/enqueue`, {
        method:"POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({payload, type}),
    });
    if(!result.ok) throw new Error(`ERROR: Failed to enqueue new job with payload: ${payload} and type: ${type}`);
    return await result.json();
}

export const deleteJob = async(id: string) => {
    const result = await fetch(`${API_BASE}/api/jobs/${id}`, {
        method:"DELETE"
    });
    if(!result.ok) throw new Error(`ERROR: Failed to delete the specific Job (ID:${id})`);
    return await result.json();
}

export const retryJob = async(id: string) => {
    const result = await fetch(`${API_BASE}/api/jobs/${id}/retry`, {
        method:"POST"
    });
    if(!result.ok) throw new Error(`ERROR: Failed to retry the job (w/ ID: ${id})`);
    return await result.json();
}

export const clearQueue = async() => {
    const result = await fetch(`${API_BASE}/api/clear`, {
        method:"POST"
    });
    if(!result.ok) throw new Error(`ERROR: Failed to clear the queue`);
    return await result.json();
}