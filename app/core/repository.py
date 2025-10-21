from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.database_models import EntryDB
from app.domain.models import Entry, EntryCreate, EntryUpdate


class EntryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, entry_data: EntryCreate, owner_id: int = 1) -> Entry:
        db_entry = EntryDB(
            owner_id=owner_id,
            title=entry_data.title,
            kind=entry_data.kind,
            link=entry_data.link,
            status=entry_data.status,
        )
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        return self._to_domain(db_entry)

    def get_by_id(self, entry_id: int) -> Optional[Entry]:
        stmt = select(EntryDB).where(EntryDB.id == entry_id)
        result = self.db.execute(stmt)
        db_entry = result.scalar_one_or_none()
        return self._to_domain(db_entry) if db_entry else None

    def get_all(self, status: Optional[str] = None) -> List[Entry]:
        stmt = select(EntryDB)
        if status:
            stmt = stmt.where(EntryDB.status == status)
        result = self.db.execute(stmt)
        db_entries = result.scalars().all()
        return [self._to_domain(entry) for entry in db_entries]

    def update(self, entry_id: int, update_data: EntryUpdate) -> Optional[Entry]:
        stmt = select(EntryDB).where(EntryDB.id == entry_id)
        result = self.db.execute(stmt)
        db_entry = result.scalar_one_or_none()

        if not db_entry:
            return None

        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_entry, field, value)

        self.db.commit()
        self.db.refresh(db_entry)
        return self._to_domain(db_entry)

    def delete(self, entry_id: int) -> bool:
        stmt = select(EntryDB).where(EntryDB.id == entry_id)
        result = self.db.execute(stmt)
        db_entry = result.scalar_one_or_none()

        if not db_entry:
            return False

        self.db.delete(db_entry)
        self.db.commit()
        return True

    def _to_domain(self, db_entry: EntryDB) -> Entry:
        return Entry(
            id=db_entry.id,
            owner_id=db_entry.owner_id,
            title=db_entry.title,
            kind=db_entry.kind,
            link=db_entry.link,
            status=db_entry.status,
        )
