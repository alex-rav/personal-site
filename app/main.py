from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routers import pages
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.database import SessionLocal
from app.models import Page

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Site")

app.include_router(pages.router)

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/{slug}")
def render_page(slug: str, request: Request):

    db = SessionLocal()
    page = db.query(Page).filter(Page.slug == slug).first()
    db.close()

    if not page:
        return {"error": "Page not found"}

    return templates.TemplateResponse(
        "page.html",
        {
            "request": request,
            "title": page.title,
            "content": page.content,
        }
    )
