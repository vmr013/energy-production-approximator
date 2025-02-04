import enum
import uuid
from typing import Union
from sqlalchemy import Column, Float, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
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

    config: Mapped[Union["SolarPowerPlantConfig", "WindPowerPlantConfig"]] = relationship(
        "SolarPowerPlantConfig",
        "WindPowerPlantConfig",
        back_populates="power_plants",
        cascade="all, delete-orphan",
        primaryjoin="and_(PowerPlant.id == SolarPowerPlantConfig.power_plant_id,"
                    f" PowerPlant.category={PowerPlantCategory.SOLAR.value})",
        secondaryjoin="and_(PowerPlant.id == WindPowerPlantConfig.power_plant_id,"
                      f" PowerPlant.category={PowerPlantCategory.SOLAR.value})"
    )

    def __repr__(self) -> str:
        return f"PowerPlant(id={self.id!r}, name={self.name!r}, model={self.model!r}, category={self.category!r})"


class SolarPowerPlantConfig(Base):
    __tablename__ = "solar_power_plant_configs"
    power_plant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("power_plants.id"), primary_key=True)
    power_plant: Mapped["PowerPlant"] = relationship(
        back_populates="solar_power_plant_configs"
    )
    total_capacity: Mapped[float] = mapped_column(Float(32), nullable=True)
    module_count: Mapped[int] = mapped_column(nullable=False)
    module_power: Mapped[int] = mapped_column(nullable=False)
    inverter_model: Mapped[str] = mapped_column(String(30), nullable=True)
    inverter_count: Mapped[int] = mapped_column(nullable=False)
    inverter_power: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return (
            f"SolarPowerPlantConfig("
            f"power_plant_id={self.power_plant_id!r}, "
            f"total_capacity={self.total_capacity!r}, "
            f"module_count={self.module_count!r}, "
            f"module_power={self.module_power!r}, "
            f"inverter_model={self.inverter_model!r}, "
            f"inverter_count={self.inverter_count!r}, "
            f"inverter_power={self.inverter_power!r}, "
            f")"
        )


class WindPowerPlantConfig(Base):
    __tablename__ = "wind_power_plant_configs"
    power_plant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("power_plants.id"), primary_key=True)
    power_plant: Mapped["PowerPlant"] = relationship(
        back_populates="wind_power_plant_configs"
    )
    production_year: Mapped[int | None]
    tower_height: Mapped[float] = Column(Float(8))
    rotor_diameter: Mapped[float] = Column(Float(8))
    start_speed: Mapped[float] = Column(Float(8))
    stop_speed: Mapped[float] = Column(Float(8))
    max_speed_limit: Mapped[float] = Column(Float(8))

    def __repr__(self) -> str:
        return (
            f"WindPowerPlantConfig("
            f"power_plant_id={self.power_plant_id!r}, "
            f"production_year={self.production_year!r}, "
            f"tower_height={self.tower_height!r}, "
            f"rotor_diameter={self.rotor_diameter!r}, "
            f"start_speed={self.start_speed!r}, "
            f"stop_speed={self.stop_speed!r}, "
            f"max_speed_limit={self.max_speed_limit!r}, "
            f")")


__all__ = [
    "PowerPlant",
]
