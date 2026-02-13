from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Page
from app.schemas import PageCreate, PageResponse

router = APIRouter(prefix="/pages", tags=["pages"])


@router.post("/", response_model=PageResponse)
def create_page(page: PageCreate, db: Session = Depends(get_db)):

    existing_page = db.query(Page).filter(Page.slug == page.slug).first()
    if existing_page:
        raise HTTPException(status_code=400, detail="Slug already exists")

    db_page = Page(**page.model_dump())
    db.add(db_page)
    db.commit()
    db.refresh(db_page)

    return db_page


@router.get("/{slug}", response_model=PageResponse)
def get_page(slug: str, db: Session = Depends(get_db)):

    page = db.query(Page).filter(Page.slug == slug).first()

    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    return page
