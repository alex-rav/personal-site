from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import engine
from app.database import SessionLocal
from app.models import Base
from app.models import Page
from app.routers import pages

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Site")

app.include_router(pages.router)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

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

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )