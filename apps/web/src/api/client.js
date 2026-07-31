const API_BASE = import.meta.env.VITE_API_BASE || "";

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }
  return response.json();
}

export function generateLc(seed) {
  return apiFetch("/api/generate", {
    method: "POST",
    body: JSON.stringify({ seed }),
  });
}

export function translateMtToMx(mt700) {
  return apiFetch("/api/mt-to-mx", {
    method: "POST",
    body: JSON.stringify({ mt700 }),
  });
}

export function validateMt(mt700) {
  return apiFetch("/api/validate-mt", {
    method: "POST",
    body: JSON.stringify({ mt700 }),
  });
}

export function validateMx(mxXml) {
  return apiFetch("/api/validate-mx", {
    method: "POST",
    body: JSON.stringify({ mx_xml: mxXml }),
  });
}
