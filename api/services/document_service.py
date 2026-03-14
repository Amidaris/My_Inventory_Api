from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
import os
import shutil
import uuid
from api.models.db_document import DocumentDB
from api.config.settings import settings


ALLOWED_FILE_TYPES = [
    # common mime types; add more as needed
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
]
ALLOWED_RELATED_TYPES = {"client", "invoice"}


def get_user_documents(db: Session, user_id: int, file_type: str = None):
    """ 
    Fetch all documents belonging to a specific user. 
    """

    query = db.query(DocumentDB).filter(DocumentDB.user_id == user_id)
    if file_type is not None:
        query = query.filter(DocumentDB.related_type == file_type)
    return query.all()


def create_document(
    db: Session,
    user_id: int,
    file: UploadFile,
    related_type: str,
    related_id: int,
):
    """Save uploaded file to storage and create metadata record.

    Raises HTTPException on validation errors.
    """

    # validate related type
    if related_type not in ALLOWED_RELATED_TYPES:
        raise HTTPException(
            status_code=400, detail=f"relatedType must be one of {ALLOWED_RELATED_TYPES}"
        )

    # simple content type validation
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}",
        )

    # ensure storage directory exists
    storage_dir = settings.DOCUMENTS_DIR
    os.makedirs(storage_dir, exist_ok=True)

    # generate unique filename to avoid clashes
    # sanitize filename to avoid path traversal
    original_name = os.path.basename(file.filename or "")
    unique_name = f"{uuid.uuid4().hex}_{original_name}"
    # physical path used for writing
    destination_path = os.path.join(storage_dir, unique_name)

    try:
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to save file"
        )
    finally:
        file.file.close()

    # path stored in database should be URL-friendly (forward slashes)
    stored_path = f"{storage_dir}/{unique_name}".replace("\\", "/")

    new_doc = DocumentDB(
        user_id=user_id,
        related_type=related_type,
        related_id=related_id,
        file_nem=file.filename,
        file_path=stored_path,
        mime_type=file.content_type or "application/octet-stream",
    )

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return new_doc
