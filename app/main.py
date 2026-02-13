from fastapi import FastAPI
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Site")

@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}
