import os
import requests

class SupabaseError(Exception):
    pass

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY", "")
        self.app_key = os.getenv("JUICECRAFT_APP_KEY", "")
        if not self.url or not self.anon_key or not self.app_key:
            raise SupabaseError("Supabase is not configured.")

    @property
    def headers(self):
        return {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.anon_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
            "x-app-api-key": self.app_key,
        }

    def request(self, method, path, params=None, json=None):
        r = requests.request(method, f"{self.url}/rest/v1/{path}", headers=self.headers, params=params, json=json, timeout=20)
        if not r.ok:
            try:
                body = r.json()
                msg = body.get("message") or body.get("hint") or r.text
            except Exception:
                msg = r.text
            raise SupabaseError(msg or f"Supabase request failed ({r.status_code})")
        return None if not r.content else r.json()

    def select(self, table, select="*", filters=None, order=None, limit=None):
        params = {"select": select}
        if filters: params.update(filters)
        if order: params["order"] = order
        if limit: params["limit"] = str(limit)
        return self.request("GET", table, params=params)

    def insert(self, table, data):
        return self.request("POST", table, json=data)

    def update(self, table, data, filters):
        return self.request("PATCH", table, params=filters, json=data)

    def rpc(self, fn, payload):
        return self.request("POST", f"rpc/{fn}", json=payload)
