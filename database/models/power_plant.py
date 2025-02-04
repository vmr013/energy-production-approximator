import enum
import uuid
from sqlalchemy import Column, Float, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .base import Base


class PowerPlantCategory(enum.Enum):
    SOLAR = 'SOLAR'
    EOLIAN = 'EOLIAN'


class PowerPlant(Base):
    __tablename__ = "power_plants"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String(30))
    model: Mapped[str | None] = mapped_column(String(30))
    longitude: Mapped[float] = mapped_column(Float(8), nullable=False)
    latitude: Mapped[float] = mapped_column(Float(8), nullable=False)
    category: Mapped[PowerPlantCategory]
    power: Mapped[float]

    def __repr__(self) -> str:
        return f"PowerPlant(id={self.id!r}, name={self.name!r}, model={self.model!r}, category={self.category!r})"


__all__ = [
    "PowerPlant",
]
