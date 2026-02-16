from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import engine
from app.database import SessionLocal
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Site")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/",  name="index")
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/skills",  name="skills")
def skills(request: Request):
    return templates.TemplateResponse(
        "skills.html",
        {"request": request}
    )

@app.get("/projects", name="projects")
def projects(request: Request):
    return templates.TemplateResponse(
        "projects.html",
        {"request": request}
    )

@app.get("/about", name="about")
def about(request: Request):
    return templates.TemplateResponse(
        "about.html",
        {"request": request}
    )