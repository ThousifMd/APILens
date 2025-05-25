import os
import psycopg2
from psycopg2 import sql

class _APILogger:
    """
    Logs API calls into a Postgres database.
    """
    def __init__(self, db_url: str = None):
        # Read and validate the database URL
        self.db_url = db_url or os.getenv("POSTGRES_DB_URL")
        if not self.db_url:
            raise RuntimeError("POSTGRES_DB_URL environment variable is required")

        # Establish connection
        self.conn = psycopg2.connect(self.db_url)
        self._ensure_table()

    def _format_cost(self, cost: float) -> str:
        return f"${cost:.6f}" if cost is not None else None

    def _ensure_table(self):
        # Create table with proper timestamp type and indexes
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS api_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
                    provider TEXT,
                    model TEXT,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    cost REAL,
                    formatted_cost TEXT,
                    status TEXT,
                    error_message TEXT,
                    user_id TEXT,
                    tenant_id TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_api_logs_tenant ON api_logs (tenant_id);
                CREATE INDEX IF NOT EXISTS idx_api_logs_time ON api_logs (timestamp);
            """)
            self.conn.commit()

    def log_call(
        self,
        call_id: int = None,
        provider: str = None,
        model: str = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost: float = 0.0,
        status: str = "pending",
        error_message: str = None,
        user_id: str = None,
        tenant_id: str = None,
    ) -> int:
        formatted = self._format_cost(cost)
        try:
            with self.conn.cursor() as cur:
                if call_id is None:
                    cur.execute(
                        sql.SQL(
                            """
                            INSERT INTO api_logs 
                              (provider, model, prompt_tokens, completion_tokens, cost, formatted_cost, status, error_message, user_id, tenant_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                            """
                        ),
                        (provider, model, prompt_tokens, completion_tokens, cost, formatted, status, error_message, user_id, tenant_id)
                    )
                    new_id = cur.fetchone()[0]
                    self.conn.commit()
                    return new_id
                else:
                    cur.execute(
                        sql.SQL(
                            """
                            UPDATE api_logs
                            SET prompt_tokens      = %s,
                                completion_tokens  = %s,
                                cost               = %s,
                                formatted_cost     = %s,
                                status             = %s,
                                error_message      = %s,
                                user_id            = %s,
                                tenant_id          = %s
                            WHERE id = %s
                            RETURNING id
                            """
                        ),
                        (prompt_tokens, completion_tokens, cost, formatted, status, error_message, user_id, tenant_id, call_id)
                    )
                    updated_id = cur.fetchone()[0]
                    self.conn.commit()
                    return updated_id
        except Exception:
            # In production, you might retry or buffer locally
            self.conn.rollback()
            raise

    def close(self):
        """Explicitly close the DB connection"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Usage example:
# with _APILogger() as logger:
#     id1 = logger.log_call(provider="openai", model="gpt-4o", prompt_tokens=10, completion_tokens=20, cost=0.001)
#     logger.log_call(call_id=id1, status="success")
