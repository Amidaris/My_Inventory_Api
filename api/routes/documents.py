from fastapi import Depends, APIRouter, status, Query, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from api.config.db import get_db
from api.models.db_user import UserDB
from api.services.auth_service import get_current_active_user
from api.services.document_service import get_user_documents, create_document
from api.models.document import Document
from typing import List


ALLOWED_RELATED_TYPES = {"client", "invoice", "waste_card"}


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get("/",
            response_model=List[Document],
            status_code=status.HTTP_200_OK,
            summary="Get documents",
            description="""
    Get documents belonging to the authenticated user.

        - Requires JWT authentication.    
        - Returns 200 with the documents.
    """
            )
async def get_documents(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
    file_type: str = Query(None, alias="type"),
):

    return get_user_documents(db, current_user.id, file_type)


@router.post("/",
             response_model=Document,
             status_code=status.HTTP_201_CREATED,
             summary="Upload document",
             description="""
    Upload a file and attach it to the authenticated user.

        - Requires JWT authentication.
        - Form parameters: file (binary), relatedType (client|invoice|waste_card), relatedId (int)
        - Stores file on disk and saves metadata to database.
        - Returns 201 with the created document record.
    """
             )
async def upload_document(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
    file: UploadFile = File(...),
    related_type: str = Form(..., alias="relatedType"),
    related_id: int = Form(..., alias="relatedId"),
):
    # basic validation for form fields
    if related_type not in ALLOWED_RELATED_TYPES:
        raise HTTPException(
            status_code=400, detail=f"relatedType must be one of {ALLOWED_RELATED_TYPES}")

    return create_document(
        db=db,
        user_id=current_user.id,
        file=file,
        related_type=related_type,
        related_id=related_id,
    )
