import os

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.auth import verify_password
from app.database import get_db
from app.models import Review, User

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError('SECRET_KEY is not set. Add it to environment variables or .env file.')

app = FastAPI(title='Personal Site')
templates = Jinja2Templates(directory='templates')

app.mount('/static', StaticFiles(directory='static'), name='static')

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@app.get('/', name='index')
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.get('/skills', name='skills')
def skills(request: Request):
    return templates.TemplateResponse('skills.html', {'request': request})


@app.get('/projects', name='projects')
def projects(request: Request):
    return templates.TemplateResponse('projects.html', {'request': request})


@app.get('/projects/{project_id}', name='project_details')
def project_details(request: Request, project_id: str):
    return templates.TemplateResponse('project.html', {'request': request, 'project_id': project_id})


@app.get('/about', name='about')
def about(request: Request):
    return templates.TemplateResponse('about.html', {'request': request})


@app.post('/login')
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')

    request.session['user_id'] = user.id
    return {'message': 'Logged in'}


def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401)

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401)

    return user


@app.get('/admin/reviews')
def admin_reviews(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(status_code=403)

    return db.query(Review).all()
