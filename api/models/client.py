import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, field_serializer


class ClientBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: str
    nip: str
    account_number: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not re.fullmatch(r"\+?\d{9,15}", v):
            raise ValueError("Invalid phone number")
        return v

    @field_validator("nip")
    @classmethod
    def validate_nip(cls, v: str) -> str:
        nip = v.replace("-", "").strip()

        if not nip.isdigit() or len(nip) != 10:
            raise ValueError("NIP must contain exactly 10 digits")

        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11

        if checksum == 10 or checksum != int(nip[9]):
            raise ValueError("Invalid NIP checksum")

        return nip


class ClientRead(ClientBase):
    id: int
    user_id: int

    @field_serializer("nip")
    def serialize_nip(self, value: str) -> str:
        # Format NIP with hyphens: 1234563218 -> 123-456-32-18
        if len(value) == 10:
            return f"{value[:3]}-{value[3:6]}-{value[6:8]}-{value[8:]}"
        return value

    model_config = {
        "from_attributes": True
    }


ClientCreate = ClientBase
ClientUpdate = ClientBase


class ClientNIPRequest(BaseModel):
    nip: str


class ClientListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[ClientRead]
