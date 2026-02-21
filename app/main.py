import os
import time
from datetime import datetime, timezone
from collections import defaultdict, deque

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.middleware.sessions import SessionMiddleware

from app.auth import verify_password
from app.database import engine, get_db
from app.models import Message, Review, User

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError('SECRET_KEY is not set. Add it to environment variables or .env file.')

app = FastAPI(title='Personal Site')
templates = Jinja2Templates(directory='templates')

app.mount('/static', StaticFiles(directory='static'), name='static')
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

RATE_LIMITS = defaultdict(deque)


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get('x-forwarded-for')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.client.host if request.client else 'unknown'


def check_rate_limit(request: Request, scope: str, limit: int, window_seconds: int) -> None:
    now = time.time()
    key = f'{scope}:{get_client_ip(request)}'
    bucket = RATE_LIMITS[key]

    while bucket and now - bucket[0] > window_seconds:
        bucket.popleft()

    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail='Too many requests. Try again later.')

    bucket.append(now)


def get_csrf_token(request: Request) -> str:
    token = request.session.get('csrf_token')
    if not token:
        token = os.urandom(24).hex()
        request.session['csrf_token'] = token
    return token


def verify_csrf(request: Request, csrf_token: str) -> None:
    session_token = request.session.get('csrf_token')
    if not session_token or csrf_token != session_token:
        raise HTTPException(status_code=403, detail='Invalid CSRF token')


@app.get('/healthz', name='healthz')
def healthz():
    try:
        with engine.connect() as connection:
            connection.execute(text('SELECT 1'))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail='Database unavailable')

    return {'status': 'ok'}


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
    return templates.TemplateResponse(
        'about.html',
        {
            'request': request,
            'csrf_token': get_csrf_token(request),
            'message_sent': request.query_params.get('message_sent') == '1',
            'message_error': request.query_params.get('message_error') == '1',
        },
    )


@app.get('/reviews', name='reviews_page')
def reviews_page(request: Request, db: Session = Depends(get_db)):
    approved_reviews = []
    try:
        approved_reviews = (
            db.query(Review)
            .filter(Review.status == 'approved')
            .order_by(Review.created_at.desc())
            .all()
        )
    except SQLAlchemyError:
        approved_reviews = []

    return templates.TemplateResponse(
        'reviews.html',
        {
            'request': request,
            'csrf_token': get_csrf_token(request),
            'approved_reviews': approved_reviews,
            'review_sent': request.query_params.get('review_sent') == '1',
            'review_error': request.query_params.get('review_error') == '1',
        },
    )


@app.post('/reviews', name='submit_review')
def submit_review(
    request: Request,
    csrf_token: str = Form(...),
    author_name: str = Form(...),
    text: str = Form(...),
    rating: int = Form(...),
    db: Session = Depends(get_db),
):
    verify_csrf(request, csrf_token)
    check_rate_limit(request, 'submit_review', limit=10, window_seconds=60)

    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail='Rating must be between 1 and 5')

    try:
        db.add(Review(author_name=author_name.strip(), text=text.strip(), rating=rating, status='pending', created_at=datetime.now(timezone.utc)))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return RedirectResponse(url='/reviews?review_error=1', status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse(url='/reviews?review_sent=1', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/messages', name='send_message')
def send_message(
    request: Request,
    csrf_token: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    verify_csrf(request, csrf_token)
    check_rate_limit(request, 'send_message', limit=10, window_seconds=60)

    try:
        db.add(Message(name=name.strip(), email=email.strip(), message=message.strip(), status='new', created_at=datetime.now(timezone.utc)))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return RedirectResponse(url='/about?message_error=1', status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse(url='/about?message_sent=1', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/admin/login', name='admin_login_page')
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        'admin_login.html',
        {
            'request': request,
            'csrf_token': get_csrf_token(request),
            'error': request.query_params.get('error') == '1',
            'db_error': request.query_params.get('db_error') == '1',
        },
    )


@app.post('/login')
def login(
    request: Request,
    csrf_token: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    verify_csrf(request, csrf_token)
    check_rate_limit(request, 'login', limit=8, window_seconds=60)

    try:
        user = db.query(User).filter(User.username == username).first()
    except SQLAlchemyError:
        return RedirectResponse('/admin/login?db_error=1', status_code=status.HTTP_303_SEE_OTHER)

    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse('/admin/login?error=1', status_code=status.HTTP_303_SEE_OTHER)

    request.session['user_id'] = user.id
    return RedirectResponse('/admin', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/logout', name='logout')
def logout(request: Request, csrf_token: str = Form(...)):
    verify_csrf(request, csrf_token)
    request.session.clear()
    return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)


def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401)

    try:
        user = db.get(User, user_id)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail='Database unavailable')

    if not user:
        raise HTTPException(status_code=401)

    return user


@app.get('/admin', name='admin_dashboard')
def admin_dashboard(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(status_code=403)

    try:
        pending_reviews = db.query(Review).filter(Review.status == 'pending').order_by(Review.created_at.desc()).all()
        all_messages = db.query(Message).order_by(Message.created_at.desc()).all()
    except SQLAlchemyError:
        pending_reviews = []
        all_messages = []

    return templates.TemplateResponse(
        'admin.html',
        {
            'request': request,
            'csrf_token': get_csrf_token(request),
            'pending_reviews': pending_reviews,
            'all_messages': all_messages,
            'user': user,
        },
    )


@app.post('/admin/reviews/{review_id}/status', name='update_review_status')
def update_review_status(
    request: Request,
    review_id: int,
    csrf_token: str = Form(...),
    new_status: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_csrf(request, csrf_token)
    if not user.is_admin:
        raise HTTPException(status_code=403)

    if new_status not in {'approved', 'rejected', 'pending'}:
        raise HTTPException(status_code=400, detail='Invalid status')

    review = db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail='Review not found')

    review.status = new_status
    db.commit()

    return RedirectResponse('/admin', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/admin/messages/{message_id}/read', name='mark_message_read')
def mark_message_read(
    request: Request,
    message_id: int,
    csrf_token: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_csrf(request, csrf_token)
    if not user.is_admin:
        raise HTTPException(status_code=403)

    message = db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail='Message not found')

    message.status = 'read'
    db.commit()

    return RedirectResponse('/admin', status_code=status.HTTP_303_SEE_OTHER)
