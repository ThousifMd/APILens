import requests
import os

class APILoggerREST:
    def __init__(self, api_url=None):
        self.api_url = api_url or os.getenv("LOG_API_URL", "http://localhost:8000/log")

    def log_call(self, **log_data):
        try:
            requests.post(self.api_url, json=log_data, timeout=3)
        except Exception as e:
            print(f"Failed to log: {e}") 