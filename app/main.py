from fastapi import FastAPI

app = FastAPI(title="Personal Site")

@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}
