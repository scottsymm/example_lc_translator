const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export function listRecords(params = {}) {
  const search = new URLSearchParams();
  if (params.offset) search.set("offset", String(params.offset));
  if (params.limit) search.set("limit", String(params.limit));
  if (params.source_type) search.set("source_type", params.source_type);
  return fetchJson(`/records?${search.toString()}`);
}

export function getRecord(id) {
  return fetchJson(`/records/${id}`);
}

export function createRecord(record) {
  return fetchJson("/records", {
    method: "POST",
    body: JSON.stringify(record),
  });
}

export function updateRecord(id, updates) {
  return fetchJson(`/records/${id}`, {
    method: "PUT",
    body: JSON.stringify(updates),
  });
}

export function deleteRecord(id) {
  return fetchJson(`/records/${id}`, {
    method: "DELETE",
  });
}
