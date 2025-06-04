import os
import logging
import psycopg2
from psycopg2.extras import Json
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

class APILoggerREST:
    def __init__(self, api_url=None):
        self.api_url = api_url or os.getenv("POSTGRES_DB_URL")
        logger.info(f"Initialized APILoggerREST with URL: {self.api_url}")
        # Ensure the table exists with both timestamps
        from .db import DB
        DB.create_api_logs_table(self.api_url)

    def log_call(self, **log_data):
        print("Attempting to log to DB...", flush=True)
        # Ensure user_id and tenant_id are strings, not None
        if log_data.get("user_id") is None:
            log_data["user_id"] = ""
        if log_data.get("tenant_id") is None:
            log_data["tenant_id"] = ""

        try:
            print("Connecting to DB with URL:", self.api_url, flush=True)
            # Connect to PostgreSQL
            conn = psycopg2.connect(self.api_url)
            cur = conn.cursor()
            print("Connected to DB, inserting log...", flush=True)

            # Get current time in both IST and CST
            now = datetime.now(pytz.UTC)
            ist_time = now.astimezone(pytz.timezone('Asia/Kolkata'))
            cst_time = now.astimezone(pytz.timezone('America/Chicago'))

            # Insert the log data with both timestamps
            cur.execute("""
                INSERT INTO api_logs (
                    created_at_ist, created_at_cst,
                    provider, model, prompt_tokens, 
                    completion_tokens, cost, status, error_message, 
                    user_id, tenant_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
            """, (
                ist_time, cst_time,
                log_data.get("provider"),
                log_data.get("model"),
                log_data.get("prompt_tokens"),
                log_data.get("completion_tokens"),
                log_data.get("cost"),
                log_data.get("status"),
                log_data.get("error_message"),
                log_data.get("user_id"),
                log_data.get("tenant_id")
            ))

            # Get the inserted ID
            log_id = cur.fetchone()[0]
            print("Log inserted with ID:", log_id, flush=True)

            # Commit the transaction
            conn.commit()

            # Close the connection
            cur.close()
            conn.close()

            logger.debug(f"Log sent successfully. ID: {log_id}")
            return log_id

        except Exception as e:
            print("DB LOGGING ERROR:", e, flush=True)
            logger.error(f"Failed to send log: {str(e)}")
            return None 