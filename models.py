from typing import Optional
import uuid
from pydantic import BaseModel, Field

class PyUUID:
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, uuid.UUID):
            return v
        if isinstance(v, str):
            try:
                return uuid.UUID(v)
            except ValueError:
                raise ValueError("Invalid UUID format")
        raise ValueError("Invalid type for UUID")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string", format="uuid")

class YugabyteBaseModel(BaseModel):
    id: PyUUID = Field(default_factory=lambda: uuid.uuid4(), alias="_id")
    
    class Config:
        json_encoders = {uuid.UUID: str, PyUUID: str}

class CarBase(YugabyteBaseModel):
    brand: str = Field(..., min_length=3)
    make: str = Field(..., min_length=3)
    year: int = Field(...)
    price: int = Field(...)
    km: int = Field(...)
    cm3: int = Field(...)

class CarUpdate(YugabyteBaseModel):
    price: Optional[int] = None

class CarDB(CarBase):
    pass
