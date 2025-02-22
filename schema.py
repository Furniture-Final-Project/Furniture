from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import String, Float, Integer, JSON, create_engine
from typing import Optional, Dict
import dataclasses
import copy

class Base(DeclarativeBase):
    def to_dict(self):
        phase1 = {key: value for (key, value) in self.__dict__.items() if not key.startswith('_')}
        phase2 = copy.deepcopy(phase1)
        return phase2


class Furniture(Base):
    __tablename__ = "furniture"
    
    model_num: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    dimensions: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    details: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    image_filename: Mapped[str] = mapped_column(String, nullable=False)
    discount: Mapped[float] = mapped_column(Float, nullable=False)


_engine = None
_session_maker = None

# Database setup
def create(filename):
    global _engine
    global _session_maker
    db_url = f"sqlite:///{filename}"
    _engine = create_engine(db_url, echo=True)
    _session_maker = sessionmaker(bind=_engine)
    Base.metadata.create_all(_engine)

def session():
    return _session_maker()

