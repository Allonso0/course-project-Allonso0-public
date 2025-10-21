from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import NotFoundError
from app.core.repository import EntryRepository
from app.core.security import ENDPOINT_LIMITS, limiter
from app.domain.models import Entry, EntryCreate, EntryStatus, EntryUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=Entry,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую запись",
)
@limiter.limit(
    ENDPOINT_LIMITS["create_entry"] if ENDPOINT_LIMITS["create_entry"] else None
)
async def create_entry(
    request: Request, entry_data: EntryCreate, db: Session = Depends(get_db)
) -> Entry:
    repository = EntryRepository(db)
    return repository.create(entry_data)


@router.get("/", response_model=List[Entry], summary="Получить список записей")
@limiter.limit(
    ENDPOINT_LIMITS["get_entries"] if ENDPOINT_LIMITS["get_entries"] else None
)
async def get_entries(
    request: Request,
    status: Optional[EntryStatus] = Query(None, description="Фильтр по статусу"),
    db: Session = Depends(get_db),
) -> List[Entry]:
    repository = EntryRepository(db)
    return repository.get_all(status.value if status else None)


@router.get("/{entry_id}", response_model=Entry, summary="Получить запись по ID")
@limiter.limit(ENDPOINT_LIMITS["get_entry"] if ENDPOINT_LIMITS["get_entry"] else None)
async def get_entry(
    request: Request, entry_id: int, db: Session = Depends(get_db)
) -> Entry:
    repository = EntryRepository(db)
    entry = repository.get_by_id(entry_id)
    if not entry:
        raise NotFoundError(f"Entry with id {entry_id}")
    return entry


@router.put("/{entry_id}", response_model=Entry, summary="Обновить запись")
@limiter.limit(
    ENDPOINT_LIMITS["update_entry"] if ENDPOINT_LIMITS["update_entry"] else None
)
async def update_entry(
    request: Request,
    entry_id: int,
    entry_data: EntryUpdate,
    db: Session = Depends(get_db),
) -> Entry:
    repository = EntryRepository(db)
    entry = repository.update(entry_id, entry_data)
    if not entry:
        raise NotFoundError(f"Entry with id {entry_id}")
    return entry


@router.delete(
    "/{entry_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить запись"
)
@limiter.limit(
    ENDPOINT_LIMITS["delete_entry"] if ENDPOINT_LIMITS["delete_entry"] else None
)
async def delete_entry(request: Request, entry_id: int, db: Session = Depends(get_db)):
    repository = EntryRepository(db)
    if not repository.delete(entry_id):
        raise NotFoundError(f"Entry with id {entry_id}")
