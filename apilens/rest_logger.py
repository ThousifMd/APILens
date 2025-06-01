import requests
import os

class APILoggerREST:
    def __init__(self, api_url=None):
        self.api_url = api_url or os.getenv("LOG_API_URL", "http://localhost:8000/log")

    def log_call(self, **log_data):
        # Ensure user_id and tenant_id are strings, not None
        if log_data.get("user_id") is None:
            log_data["user_id"] = ""
        if log_data.get("tenant_id") is None:
            log_data["tenant_id"] = ""
        print(f"[REST Logger] Sending log to {self.api_url} with data: {log_data}")
        try:
            response = requests.post(self.api_url, json=log_data, timeout=3)
            print(f"[REST Logger] Response status: {response.status_code}, body: {response.text}")
        except Exception as e:
            print(f"[REST Logger] Failed to log: {e}") 