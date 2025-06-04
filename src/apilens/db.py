import sqlite3
from .config import DB_PATH
import psycopg2
from datetime import datetime
import pytz

class DB:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, isolation_level=None)

    def query(self, sql, params=None):
        cur = self.conn.cursor()
        cur.execute(sql, params or ())
        return cur.fetchall()

    def close(self):
        self.conn.close()

    @staticmethod
    def create_api_logs_table(db_url):
        """Create or update the api_logs table with both IST and CST timestamps"""
        try:
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            
            # Create the table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS api_logs (
                    id SERIAL PRIMARY KEY,
                    created_at_ist TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata'),
                    created_at_cst TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Chicago'),
                    provider VARCHAR(50),
                    model VARCHAR(100),
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    cost DECIMAL(10, 6),
                    status VARCHAR(20),
                    error_message TEXT,
                    user_id VARCHAR(100),
                    tenant_id VARCHAR(100)
                )
            """)
            
            # Add IST column if it doesn't exist
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'api_logs' 
                        AND column_name = 'created_at_ist'
                    ) THEN
                        ALTER TABLE api_logs ADD COLUMN created_at_ist TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata');
                    END IF;
                END $$;
            """)
            
            # Add CST column if it doesn't exist
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'api_logs' 
                        AND column_name = 'created_at_cst'
                    ) THEN
                        ALTER TABLE api_logs ADD COLUMN created_at_cst TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Chicago');
                    END IF;
                END $$;
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating/updating api_logs table: {str(e)}")
            return False

    # Placeholder for future Postgres support
