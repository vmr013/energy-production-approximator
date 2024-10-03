from typing import Literal

from pydantic import RootModel, Field, BaseModel, PositiveInt, NonNegativeFloat, PositiveFloat


def get_power_plants(file_path='plants.json'):
    with open(file_path) as f:
        return PowerPlants.model_validate_json(f.read())


class GeoLocation(BaseModel):
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)

    @property
    def string(self):
        return f"{abs(self.latitude)} {'N' if self.latitude >= 0 else 'S'}," \
               f" {abs(self.longitude)} {'E' if self.longitude >= 0 else 'W'}"


class SolarPlant(BaseModel):
    type: Literal['SOLAR']
    name: str
    installationCapacity: PositiveFloat = Field(
        title="Installation Capacity",
        description="Measured in MW (megawatts)"
    )
    totalCapacity: PositiveInt = Field(
        title="Total installation capacity",
        description="Measured in W (watts)"
    )
    numberOfModules: PositiveInt
    moduleCapacity: PositiveInt
    model: str = None
    inverter: str = None
    numberOfInverters: PositiveInt
    inverterCapacity: PositiveInt
    geolocation: GeoLocation


class WindPlant(BaseModel):
    type: Literal['WIND']
    name: str
    installationCapacity: PositiveFloat
    model: str = None
    towerHeight: PositiveInt
    rotorDiameter: PositiveInt
    startSpeed: PositiveFloat
    stopSpeed: PositiveFloat
    maxLimit: PositiveFloat
    geolocation: GeoLocation


class PowerPlants(RootModel):
    root: list[SolarPlant | WindPlant]
