import { API_BASE } from "../config";

async function handleResponse(res) {
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`API error ${res.status}: ${text}`);
    }
    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
        return res.json();
    }
    return null;
}

export async function saveRange({ cardRange, player = "default", category = "Ranges", name = "unnamed" }) {
    const url = `${API_BASE}/ranges/save`;
    const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player, category, name, cardRange }),
    });
    return handleResponse(res);
}

export async function loadRange({ player = "default", category = "Ranges", position = "UTG", name }) {
    const params = new URLSearchParams({ player, category, position, name });
    const url = `${API_BASE}/ranges/load?${params.toString()}`;
    const res = await fetch(url, { method: "GET" });
    return handleResponse(res); // expected to return the stored cardRange object
}

export async function listRanges({ player = "default", category = "Ranges", position } = {}) {
    try {
    const params = new URLSearchParams({ player, category });
    if (position) params.set("position", position);
    const url = `${API_BASE}/ranges/list?${params.toString()}`;
    const res = await fetch(url, { method: "GET" });
    return handleResponse(res);
    } catch (error) {
        console.error("Error listing ranges:", error);
        return {};
    }
}

export async function deleteRange({ player = "default", category = "Ranges", position = "UTG", name }) {
    const url = `${API_BASE}/ranges/delete`;
    const res = await fetch(url, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player, category, position, name }),
    });
    return handleResponse(res);
}

export async function getPlayers() {
    try {
        const url = `${API_BASE}/players`;
        const res = await fetch(url, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        });
        return handleResponse(res);
    } catch (error) {
        console.log(error);
        return {};
    }
}
export async function getCategories(player = "default") {
  try {
    const params = new URLSearchParams({ player });

    const url = `${API_BASE}/categories?${params.toString()}`;
    const res = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    return handleResponse(res);
  } catch (error) {
    console.log(error);
    return {};
  }
}

export async function getNames({ player = "default", category = "Ranges", position = "UTG" } = {}) {
  try {
    const params = new URLSearchParams({ player, category, position });
    const url = `${API_BASE}/names?${params.toString()}`;
    const res = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    return handleResponse(res);
  } catch (error) {
    console.log(error);
    return {};
  }
}

export async function createPlayer(name) {
    const url = `${API_BASE}/players`;
    const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
    });
    return handleResponse(res);
}

export async function createCategory(player, name) {
    const url = `${API_BASE}/categories`;
    const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player, name }),
    });
    return handleResponse(res);
}

export async function getTree(player = null) {
    const params = player ? `?player=${encodeURIComponent(player)}` : "";
    const url = `${API_BASE}/ranges/tree${params}`;
    const res = await fetch(url, { method: "GET" });
    return handleResponse(res);
}