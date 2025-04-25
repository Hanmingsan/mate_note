# backend/app/api/v1/endpoints/students.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    UploadFile, # For file uploads
    File,       # For file uploads
    Form        # For form data
)
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated # Annotated for Form fields

# Import CRUD operations instance, session dependency, schemas, and models
from app.db.crud.crud_student import crud_student
from app.db.session import get_db
from app.schemas import student as student_schemas
from app.db import models # Needed for permission checks potentially

# Import OSS service (assuming it exists for file uploads)
# You'll need to create this service/utility function
# from app.services.oss_service import upload_file_to_oss, delete_file_from_oss

# --- Mock OSS Service for demonstration ---
# Replace this with your actual OSS interaction logic
async def mock_upload_file_to_oss(file: UploadFile) -> Optional[str]:
    """Mocks uploading a file and returns a fake URL."""
    if not file or not file.filename:
        return None
    # In a real scenario, you would upload file.file (a SpooledTemporaryFile)
    # to OSS and return the actual URL.
    print(f"Mock uploading file: {file.filename}, content_type: {file.content_type}")
    # Reset file pointer in case it was read before
    await file.seek(0)
    # Example: Read content (optional, just for demo)
    # content = await file.read()
    # print(f"Mock file size: {len(content)} bytes")
    return f"https://fake-oss-bucket.endpoint/avatars/{file.filename}" # Return a fake URL

async def mock_delete_file_from_oss(file_url: Optional[str]):
    """Mocks deleting a file from OSS based on its URL."""
    if file_url:
        print(f"Mock deleting file from OSS: {file_url}")
    # In a real scenario, parse the URL to get the object key and delete from OSS
    pass
# --- End Mock OSS Service ---


# Create an API router for this endpoint file
router = APIRouter()

@router.get(
    "/",
    response_model=List[student_schemas.Student],
    summary="Get Student List",
    description="Retrieve a list of student (or teacher) records, with optional filtering and pagination.",
    tags=["Students"]
)
def read_students(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return (for pagination)"),
    name: Optional[str] = Query(None, min_length=1, max_length=100, description="Filter by name (case-insensitive partial match)"),
    position: Optional[str] = Query(None, max_length=50, description="Filter by exact position"),
    email: Optional[str] = Query(None, description="Filter by exact email"),
    db: Session = Depends(get_db)
):
    """
    API endpoint to retrieve a list of students.
    """
    students = crud_student.get_multi(
        db=db, skip=skip, limit=limit, name=name, position=position, email=email
    )
    return students

@router.get(
    "/{student_id}",
    response_model=student_schemas.Student,
    summary="Get Specific Student Information",
    description="Retrieve detailed information for a single student (or teacher) by their unique ID.",
    tags=["Students"],
    responses={404: {"description": "Student not found"}}
)
def read_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    API endpoint to retrieve a single student by ID.
    """
    db_student = crud_student.get(db=db, id=student_id)
    if db_student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return db_student

@router.post(
    "/",
    response_model=student_schemas.Student,
    status_code=status.HTTP_201_CREATED, # Set success status code to 201 Created
    summary="Add New Student",
    description="Create a new student (or teacher) record, with an optional avatar upload.",
    tags=["Students"],
    # Add responses for potential errors like validation errors
    responses={422: {"description": "Validation Error"}}
)
async def create_student( # Use async def if file operations are async
    *, # Force keyword arguments
    db: Session = Depends(get_db),
    # Use Annotated and Form for form fields
    name: Annotated[str, Form(min_length=1, max_length=100)],
    email: Annotated[Optional[str], Form()] = None,
    phone: Annotated[Optional[str], Form(max_length=20)] = None,
    address: Annotated[Optional[str], Form(max_length=255)] = None,
    wechat: Annotated[Optional[str], Form(max_length=100)] = None,
    qq: Annotated[Optional[str], Form(max_length=20)] = None,
    position: Annotated[Optional[str], Form(max_length=50)] = None,
    comments: Annotated[Optional[str], Form()] = None,
    # Use File for the optional avatar upload
    avatar: Optional[UploadFile] = File(None, description="Avatar image file")
    # TODO: Add dependency for current user if needed for authorization
):
    """
    API endpoint to create a new student record.
    Handles form data and optional file upload.
    """
    avatar_url: Optional[str] = None
    if avatar:
        # --- Replace with actual OSS upload ---
        try:
            avatar_url = await mock_upload_file_to_oss(avatar)
            # avatar_url = await upload_file_to_oss(avatar) # Your actual function
        except Exception as e:
            # Handle potential upload errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload avatar: {e}"
            )
        # --- End Replace ---

    # Create a StudentCreate schema instance from the form data
    student_in = student_schemas.StudentCreate(
        name=name,
        email=email,
        phone=phone,
        address=address,
        wechat=wechat,
        qq=qq,
        position=position,
        comments=comments
    )

    # Call the CRUD function to create the student in the database
    try:
        db_student = crud_student.create(db=db, obj_in=student_in, avatar_url=avatar_url)
    except Exception as e:
        # Handle potential database errors (e.g., unique constraint violation on email)
        # Rollback potential OSS upload if DB fails? (More complex logic needed)
        await mock_delete_file_from_oss(avatar_url) # Attempt to clean up mock upload
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # Or 500 depending on error
            detail=f"Failed to create student record: {e}"
        )
    return db_student


@router.patch(
    "/{student_id}",
    response_model=student_schemas.Student,
    summary="Update Student Information",
    description="Modify information for an existing record, supporting partial updates and avatar replacement.",
    tags=["Students"],
    responses={
        404: {"description": "Student not found"},
        403: {"description": "Not enough permissions"}, # Example permission error
        422: {"description": "Validation Error"}
    }
)
async def update_student( # Use async def if file operations are async
    *,
    db: Session = Depends(get_db),
    student_id: int,
    # Use Annotated and Form for optional update fields
    name: Annotated[Optional[str], Form(min_length=1, max_length=100)] = None,
    email: Annotated[Optional[str], Form()] = None,
    phone: Annotated[Optional[str], Form(max_length=20)] = None,
    address: Annotated[Optional[str], Form(max_length=255)] = None,
    wechat: Annotated[Optional[str], Form(max_length=100)] = None,
    qq: Annotated[Optional[str], Form(max_length=20)] = None,
    position: Annotated[Optional[str], Form(max_length=50)] = None,
    comments: Annotated[Optional[str], Form()] = None,
    # Optional new avatar file
    avatar: Optional[UploadFile] = File(None, description="New avatar image file"),
    # TODO: Add dependency for current user for permission checks
    # current_user: models.User = Depends(get_current_active_user)
):
    """
    API endpoint to update an existing student record.
    Handles partial updates via form data and optional avatar replacement.
    """
    # 1. Get the existing student record
    db_student = crud_student.get(db=db, id=student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # 2. TODO: Check permissions - does the current user have rights to update?
    # if db_student.owner_id != current_user.id and not current_user.is_superuser:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # 3. Handle potential new avatar upload
    new_avatar_url: Optional[str] = None
    old_avatar_url: Optional[str] = db_student.avatar_url # Store old URL for potential deletion
    avatar_updated = False # Flag to track if avatar processing happened

    if avatar:
        avatar_updated = True
        # --- Replace with actual OSS upload ---
        try:
            new_avatar_url = await mock_upload_file_to_oss(avatar)
            # new_avatar_url = await upload_file_to_oss(avatar)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload new avatar: {e}"
            )
        # --- End Replace ---

    # 4. Create the update schema from the provided form data
    # Only include fields that were actually sent in the form
    update_data = {
        k: v for k, v in {
            "name": name, "email": email, "phone": phone, "address": address,
            "wechat": wechat, "qq": qq, "position": position, "comments": comments
        }.items() if v is not None
    }
    student_in = student_schemas.StudentUpdate(**update_data)

    # 5. Call the CRUD update function
    try:
        updated_student = crud_student.update(
            db=db,
            db_obj=db_student,
            obj_in=student_in,
            # Pass new URL only if avatar was processed, otherwise pass None
            # to indicate no change requested via file upload this time.
            # The crud method needs to handle None correctly.
            avatar_url=new_avatar_url if avatar_updated else None
        )
    except Exception as e:
        # If DB update fails, try to rollback OSS upload
        if avatar_updated:
            await mock_delete_file_from_oss(new_avatar_url)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # Or 500
            detail=f"Failed to update student record: {e}"
        )

    # 6. If update was successful and a new avatar was uploaded, delete the old one
    if avatar_updated and old_avatar_url:
        # --- Replace with actual OSS delete ---
        await mock_delete_file_from_oss(old_avatar_url)
        # await delete_file_from_oss(old_avatar_url)
        # --- End Replace ---

    return updated_student


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT, # Standard success code for DELETE
    summary="Delete Student",
    description="Remove a student (or teacher) record by their ID.",
    tags=["Students"],
    responses={
        404: {"description": "Student not found"},
        403: {"description": "Not enough permissions"}
    }
)
async def delete_student( # Use async def if file operations are async
    *,
    db: Session = Depends(get_db),
    student_id: int,
    # TODO: Add dependency for current user for permission checks
    # current_user: models.User = Depends(get_current_active_superuser) # Example: only superuser can delete
):
    """
    API endpoint to delete a student record.
    Includes permission checks and deletion of associated avatar from OSS.
    """
    # 1. Get the student record
    db_student = crud_student.get(db=db, id=student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # 2. TODO: Check permissions
    # if not current_user.is_superuser:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # 3. Store avatar URL before deleting DB record
    avatar_url_to_delete = db_student.avatar_url

    # 4. Delete the record from the database
    deleted_student = crud_student.remove(db=db, id=student_id)
    # crud_student.remove already handles commit, no need to commit again here

    if not deleted_student:
         # This case should ideally not happen if get() succeeded, but good practice
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete student record after finding it."
        )

    # 5. If DB deletion was successful, delete avatar from OSS
    if avatar_url_to_delete:
        # --- Replace with actual OSS delete ---
        try:
            await mock_delete_file_from_oss(avatar_url_to_delete)
            # await delete_file_from_oss(avatar_url_to_delete)
        except Exception as e:
            # Log the error but don't fail the request, DB deletion was successful
            print(f"Warning: Failed to delete avatar from OSS: {avatar_url_to_delete}. Error: {e}")
        # --- End Replace ---

    # No response body needed for 204 No Content
    return None

