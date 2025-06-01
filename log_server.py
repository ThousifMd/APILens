from fastapi import FastAPI, Request, HTTPException, Query
import psycopg2
import os
from pydantic import BaseModel
from psycopg2 import DatabaseError
from typing import Optional
from datetime import datetime
import pytz

app = FastAPI()

DB_URL = os.getenv("POSTGRES_DB_URL")

class LogEntry(BaseModel):
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    status: str
    user_id: str = None
    tenant_id: str = None

@app.post("/log")
async def log_api_call(entry: LogEntry):
    cost = entry.cost
    if cost is not None:
        formatted_cost = f"{float(cost):.6f}"
    else:
        formatted_cost = None
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO api_logs (provider, model, prompt_tokens, completion_tokens, cost, formatted_cost, status, error_message, user_id, tenant_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                entry.provider,
                entry.model,
                entry.prompt_tokens,
                entry.completion_tokens,
                float(cost) if cost is not None else None,
                formatted_cost,
                entry.status,
                None,
                entry.user_id,
                entry.tenant_id
            )
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "logged"}
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))

@app.get("/logs")
async def get_logs(
    limit: int = 10,
    offset: int = 0,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        query = "SELECT * FROM api_logs WHERE 1=1"
        params = []
        if provider:
            query += " AND provider = %s"
            params.append(provider)
        if model:
            query += " AND model = %s"
            params.append(model)
        if status:
            query += " AND status = %s"
            params.append(status)
        if user_id:
            query += " AND user_id = %s"
            params.append(user_id)
        if start_time:
            query += " AND timestamp >= %s"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= %s"
            params.append(end_time)
        query += " ORDER BY id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        logs = []
        india_tz = pytz.timezone("Asia/Kolkata")
        us_cst_tz = pytz.timezone("America/Chicago")
        for row in rows:
            log = dict(zip(columns, row))
            utc_dt = log["timestamp"]
            if utc_dt and utc_dt.tzinfo is not None:
                local_dt_india = utc_dt.astimezone(india_tz)
                local_dt_us_cst = utc_dt.astimezone(us_cst_tz)
                log["local_timestamp_india"] = local_dt_india.strftime("%Y-%m-%d %H:%M:%S %Z%z")
                log["local_timestamp_us_cst"] = local_dt_us_cst.strftime("%Y-%m-%d %H:%M:%S %Z%z")
            else:
                log["local_timestamp_india"] = None
                log["local_timestamp_us_cst"] = None
            logs.append(log)
        cur.close()
        conn.close()
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 