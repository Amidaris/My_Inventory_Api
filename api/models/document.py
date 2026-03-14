
from datetime import datetime
from pydantic import BaseModel


class Document(BaseModel):
    id: int
    user_id: int
    related_type: str
    related_id: int
    file_name: str
    file_path: str
    mime_type: str
    create_at: datetime

    model_config = {
        "from_attributes": True
    }
