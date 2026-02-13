from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routers import pages

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Site")

app.include_router(pages.router)

@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}
