from fastapi import FastAPI

app = FastAPI(title="Personal Site")

@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}

from app.database import engine

@app.get("/test-db")
def test_db():
    connection = engine.connect()
    connection.close()
    return {"database": "connected"}
