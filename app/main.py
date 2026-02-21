import os

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.middleware.sessions import SessionMiddleware

from app.auth import verify_password
from app.database import get_db
from app.models import Message, Review, User

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
    return templates.TemplateResponse(
        'about.html',
        {
            'request': request,
            'message_sent': request.query_params.get('message_sent') == '1',
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
            'approved_reviews': approved_reviews,
            'review_sent': request.query_params.get('review_sent') == '1',
        },
    )


@app.post('/reviews', name='submit_review')
def submit_review(
    author_name: str = Form(...),
    text: str = Form(...),
    rating: int = Form(...),
    db: Session = Depends(get_db),
):
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail='Rating must be between 1 and 5')

    db.add(Review(author_name=author_name.strip(), text=text.strip(), rating=rating, status='pending'))
    db.commit()

    return RedirectResponse(url='/reviews?review_sent=1', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/messages', name='send_message')
def send_message(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    db.add(Message(name=name.strip(), email=email.strip(), message=message.strip(), status='new'))
    db.commit()

    return RedirectResponse(url='/about?message_sent=1', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/admin/login', name='admin_login_page')
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        'admin_login.html',
        {'request': request, 'error': request.query_params.get('error') == '1'},
    )


@app.post('/login')
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse('/admin/login?error=1', status_code=status.HTTP_303_SEE_OTHER)

    request.session['user_id'] = user.id
    return RedirectResponse('/admin', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/logout', name='logout')
def logout(request: Request):
    request.session.clear()
    return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)


def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401)

    user = db.get(User, user_id)
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

    pending_reviews = db.query(Review).filter(Review.status == 'pending').order_by(Review.created_at.desc()).all()
    all_messages = db.query(Message).order_by(Message.created_at.desc()).all()

    return templates.TemplateResponse(
        'admin.html',
        {
            'request': request,
            'pending_reviews': pending_reviews,
            'all_messages': all_messages,
            'user': user,
        },
    )


@app.post('/admin/reviews/{review_id}/status', name='update_review_status')
def update_review_status(
    review_id: int,
    new_status: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
    message_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(status_code=403)

    message = db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail='Message not found')

    message.status = 'read'
    db.commit()

    return RedirectResponse('/admin', status_code=status.HTTP_303_SEE_OTHER)
