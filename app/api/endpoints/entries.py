from typing import List, Optional

from fastapi import APIRouter, Query, Request, status

from app.core.errors import NotFoundError
from app.core.security import ENDPOINT_LIMITS, limiter
from app.domain.models import Entry, EntryCreate, EntryStatus, EntryUpdate

router = APIRouter()

# Временно.
entries_db = []
current_id = 1


def reset_database():
    global entries_db, current_id
    entries_db = []
    current_id = 1


@router.post(
    "/",
    response_model=Entry,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую запись",
)
@limiter.limit(
    ENDPOINT_LIMITS["create_entry"] if ENDPOINT_LIMITS["create_entry"] else None
)
async def create_entry(request: Request, entry_data: EntryCreate) -> Entry:
    global current_id

    entry = Entry(id=current_id, owner_id=1, **entry_data.dict())

    entries_db.append(entry)
    current_id += 1

    return entry


@router.get("/", response_model=List[Entry], summary="Получить список записей")
@limiter.limit(
    ENDPOINT_LIMITS["get_entries"] if ENDPOINT_LIMITS["get_entries"] else None
)
async def get_entries(
    request: Request,
    status: Optional[EntryStatus] = Query(None, description="Фильтр по статусу"),
) -> List[Entry]:
    if status:
        return [entry for entry in entries_db if entry.status == status]
    return entries_db


@router.get("/{entry_id}", response_model=Entry, summary="Получить запись по ID")
@limiter.limit(ENDPOINT_LIMITS["get_entry"] if ENDPOINT_LIMITS["get_entry"] else None)
async def get_entry(request: Request, entry_id: int) -> Entry:
    for entry in entries_db:
        if entry.id == entry_id:
            return entry

    raise NotFoundError(f"Entry with id {entry_id}")


@router.put("/{entry_id}", response_model=Entry, summary="Обновить запись")
@limiter.limit(
    ENDPOINT_LIMITS["update_entry"] if ENDPOINT_LIMITS["update_entry"] else None
)
async def update_entry(
    request: Request, entry_id: int, entry_data: EntryUpdate
) -> Entry:
    for index, entry in enumerate(entries_db):
        if entry.id == entry_id:
            current_data = entry.dict()
            update_data = entry_data.dict(exclude_unset=True)
            updated_data = {**current_data, **update_data}

            updated_entry = Entry(**updated_data)
            entries_db[index] = updated_entry

            return updated_entry

    raise NotFoundError(f"Entry with id {entry_id}")


@router.delete(
    "/{entry_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить запись"
)
@limiter.limit(
    ENDPOINT_LIMITS["delete_entry"] if ENDPOINT_LIMITS["delete_entry"] else None
)
async def delete_entry(request: Request, entry_id: int):
    global entries_db

    for index, entry in enumerate(entries_db):
        if entry.id == entry_id:
            entries_db.pop(index)
            return

    raise NotFoundError(f"Entry with id {entry_id}")
