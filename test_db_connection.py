import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

def test_db_connection():
    # Load environment variables
    load_dotenv()
    
    # Get database URL
    db_url = os.getenv("POSTGRES_DB_URL")
    if not db_url:
        print("Error: POSTGRES_DB_URL not found in environment variables")
        return False
    
    try:
        # Try to connect to the database
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Test the connection by creating the api_logs table
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
        
        # Test inserting a sample record
        cur.execute("""
            INSERT INTO api_logs (provider, model, prompt_tokens, completion_tokens, cost, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, ('test', 'test-model', 10, 20, 0.001, 'success'))
        
        # Commit the transaction
        conn.commit()
        
        # Verify the record was inserted
        cur.execute("SELECT COUNT(*) FROM api_logs")
        count = cur.fetchone()[0]
        print(f"Successfully connected to database. Found {count} records in api_logs table.")
        
        # Clean up
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return False

if __name__ == "__main__":
    test_db_connection() 