import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Flourisha Calculator",
    description="Calculator with calculation history",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "/code/calculator.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expression TEXT NOT NULL,
            result REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

class CalculateRequest(BaseModel):
    expression: str

class CalculateResponse(BaseModel):
    id: int
    expression: str
    result: float
    timestamp: str

class HistoryResponse(BaseModel):
    history: List[CalculateResponse]

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("/code/index.html", "r") as f:
        return f.read()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "calculator", "version": "1.0"}

@app.post("/api/calculate")
async def calculate(request: CalculateRequest):
    try:
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in request.expression):
            raise ValueError("Invalid characters")
        
        result = eval(request.expression)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO calculations (expression, result) VALUES (?, ?)", (request.expression, result))
        conn.commit()
        
        calc_id = cursor.lastrowid
        cursor.execute("SELECT * FROM calculations WHERE id = ?", (calc_id,))
        row = cursor.fetchone()
        conn.close()
        
        return CalculateResponse(id=row[0], expression=row[1], result=row[2], timestamp=row[3])
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Division by zero")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid expression: {str(e)}")

@app.get("/api/history")
async def get_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calculations ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    
    history = [CalculateResponse(id=r[0], expression=r[1], result=r[2], timestamp=r[3]) for r in rows]
    return HistoryResponse(history=history)

@app.delete("/api/history")
async def clear_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM calculations")
    count = cursor.fetchone()[0]
    cursor.execute("DELETE FROM calculations")
    conn.commit()
    conn.close()
    
    return {"message": "History cleared successfully", "deleted_count": count}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5173)
