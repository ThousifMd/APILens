from fastapi import FastAPI, Request
import psycopg2
import os

app = FastAPI()

DB_URL = os.getenv("POSTGRES_DB_URL")

@app.post("/log")
async def log_api_call(request: Request):
    data = await request.json()
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO api_logs (provider, model, prompt_tokens, completion_tokens, cost, formatted_cost, status, error_message, user_id, tenant_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data.get("provider"),
            data.get("model"),
            data.get("prompt_tokens"),
            data.get("completion_tokens"),
            data.get("cost"),
            data.get("formatted_cost"),
            data.get("status"),
            data.get("error_message"),
            data.get("user_id"),
            data.get("tenant_id"),
        )
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "logged"} 