from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EntryDB(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=False, default=1)
    title = Column(String(200), nullable=False)
    kind = Column(String(10), nullable=False)
    link = Column(Text, nullable=True)
    status = Column(String(15), nullable=False, default="planned")

    def __repr__(self):
        return f"<EntryDB(id={self.id}, title='{self.title}', kind='{self.kind}')>"
