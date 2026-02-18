from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import engine
from app.database import SessionLocal
from app.models import Base

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

from starlette.middleware.sessions import SessionMiddleware
import os

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "supersecretkey")
)

from fastapi import Form, Depends, HTTPException
from app.database import SessionLocal
from app.models import User
from app.auth import verify_password


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    request.session["user_id"] = user.id
    return {"message": "Logged in"}


from fastapi import Depends

def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401)

    db = SessionLocal()
    user = db.query(User).get(user_id)

    if not user:
        raise HTTPException(status_code=401)

    return user


@app.get("/admin/reviews")
def admin_reviews(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403)

    db = SessionLocal()
    return db.query(Review).all()
