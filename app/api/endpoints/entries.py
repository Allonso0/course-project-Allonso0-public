from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.domain.models import Entry, EntryCreate, EntryStatus, EntryUpdate

router = APIRouter()

# Временно.
entries_db = []
current_id = 1


@router.post(
    "/",
    response_model=Entry,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую запись",
    description="Создает новую запись в списке чтения",
)
async def create_entry(entry_data: EntryCreate) -> Entry:
    global current_id

    entry = Entry(id=current_id, owner_id=1, **entry_data.dict())  # Заглушка.

    entries_db.append(entry)
    current_id += 1

    return entry


@router.get(
    "/",
    response_model=List[Entry],
    summary="Получить список записей",
    description="Возвращает список всех записей с возможностью фильтрации по статусу",
)
async def get_entries(
    status: Optional[EntryStatus] = Query(None, description="Фильтр по статусу записи")
) -> List[Entry]:
    if status:
        filtered_entries = [entry for entry in entries_db if entry.status == status]
        return filtered_entries

    return entries_db


@router.get(
    "/{entry_id}",
    response_model=Entry,
    summary="Получить запись по ID",
    description="Возвращает конкретную запись по её идентификатору",
)
async def get_entry(entry_id: int) -> Entry:
    for entry in entries_db:
        if entry.id == entry_id:
            return entry

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Entry with id {entry_id} not found",
    )


@router.put(
    "/{entry_id}",
    response_model=Entry,
    summary="Обновить запись",
    description="Полностью обновляет существующую запись",
)
async def update_entry(entry_id: int, entry_data: EntryUpdate) -> Entry:
    for index, entry in enumerate(entries_db):
        if entry.id == entry_id:

            current_data = entry.dict()

            update_data = entry_data.dict(exclude_unset=True)
            updated_data = {**current_data, **update_data}

            updated_entry = Entry(**updated_data)
            entries_db[index] = updated_entry

            return updated_entry

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Entry with id {entry_id} not found",
    )


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить запись",
    description="Удаляет запись по ID",
)
async def delete_entry(entry_id: int):
    global entries_db

    for index, entry in enumerate(entries_db):
        if entry.id == entry_id:
            entries_db.pop(index)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Entry with id {entry_id} not found",
    )
