"""
Supabase Database Client for Gemini Chatbot.
Handles persisting and retrieving conversation history.
Works with both Supabase REST API (zero external dependencies) and official supabase-py SDK.
"""

import os
import json
import urllib.request
import urllib.error

# In-memory fallback if Supabase is not configured or offline
_MEMORY_STORE = {}

def get_supabase_config():
    """Retrieve Supabase URL and Key from environment."""
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_KEY", "").strip() or os.environ.get("SUPABASE_ANON_KEY", "").strip()
    return url, key

def is_supabase_enabled():
    url, key = get_supabase_config()
    return bool(url and key)

def save_message(role: str, content: str, session_id: str = "default") -> bool:
    """Save a single message to Supabase (or in-memory store)."""
    url, key = get_supabase_config()

    if not (url and key):
        if session_id not in _MEMORY_STORE:
            _MEMORY_STORE[session_id] = []
        _MEMORY_STORE[session_id].append({"role": role, "content": content})
        return True

    endpoint = f"{url}/rest/v1/messages"
    payload = {
        "session_id": session_id,
        "role": role,
        "content": content
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status in (200, 201)
    except Exception as e:
        print(f"[Supabase Warning] Failed to save message: {e}. Falling back to memory.")
        if session_id not in _MEMORY_STORE:
            _MEMORY_STORE[session_id] = []
        _MEMORY_STORE[session_id].append({"role": role, "content": content})
        return False

def get_messages(session_id: str = "default", limit: int = 50) -> list:
    """Retrieve chat history for a session from Supabase (or in-memory store)."""
    url, key = get_supabase_config()

    if not (url and key):
        return _MEMORY_STORE.get(session_id, [])

    endpoint = f"{url}/rest/v1/messages?session_id=eq.{session_id}&order=created_at.asc&limit={limit}"
    req = urllib.request.Request(
        endpoint,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        method="GET"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            records = json.loads(response.read().decode("utf-8"))
            return [{"role": r["role"], "content": r["content"]} for r in records]
    except Exception as e:
        print(f"[Supabase Warning] Failed to fetch history: {e}. Returning memory store.")
        return _MEMORY_STORE.get(session_id, [])

def clear_messages(session_id: str = "default") -> bool:
    """Clear chat history for a session."""
    url, key = get_supabase_config()

    if session_id in _MEMORY_STORE:
        _MEMORY_STORE[session_id] = []

    if not (url and key):
        return True

    endpoint = f"{url}/rest/v1/messages?session_id=eq.{session_id}"
    req = urllib.request.Request(
        endpoint,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}"
        },
        method="DELETE"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status in (200, 204)
    except Exception as e:
        print(f"[Supabase Warning] Failed to clear messages: {e}")
        return False
