# backend/app/db/crud/crud_student.py
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session
from sqlalchemy import select

# Import the generic base class
from .base import CRUDBase
# Import the SQLAlchemy model
from app.db import models
# Import the Pydantic schemas
from app.schemas import student as student_schemas


class CRUDStudent(CRUDBase[models.Student, student_schemas.StudentCreate, student_schemas.StudentUpdate]):
    """
    CRUD operations specific to the Student model.
    Inherits from CRUDBase and overrides methods as needed.
    """

    # Override get_multi to add specific filtering capabilities
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        position: Optional[str] = None,
        email: Optional[str] = None
    ) -> List[models.Student]:
        """
        Retrieves a list of student records, with specific filtering for students.

        Args:
            db: The SQLAlchemy database session.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            name: Filter by name (case-insensitive partial match).
            position: Filter by exact position.
            email: Filter by exact email.

        Returns:
            A list of matching Student ORM objects.
        """
        # Start with the base select statement for the Student model
        stmt = select(self.model).order_by(self.model.id)

        # Apply specific filters for students
        if name:
            # Using ilike for case-insensitive search (behavior might vary slightly across DB backends)
            stmt = stmt.where(self.model.name.ilike(f"%{name}%"))
        if position:
            stmt = stmt.where(self.model.position == position)
        if email:
            stmt = stmt.where(self.model.email == email)

        # Apply pagination using offset and limit
        stmt = stmt.offset(skip).limit(limit)

        # Execute the query and return all scalar results (the Student objects)
        results = db.execute(stmt).scalars().all()
        return results

    # Override create to handle the optional avatar_url
    def create(self, db: Session, *, obj_in: student_schemas.StudentCreate, avatar_url: Optional[str] = None) -> models.Student:
        """
        Creates a new student record, handling the optional avatar_url.

        Args:
            db: The SQLAlchemy database session.
            obj_in: The Pydantic schema containing the student data.
            avatar_url: The URL of the uploaded avatar, if any.

        Returns:
            The newly created Student ORM object.
        """
        # Convert Pydantic schema to dict
        obj_in_data = obj_in.model_dump()
        # Create the model instance, explicitly passing avatar_url
        db_obj = self.model(**obj_in_data, avatar_url=avatar_url)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # Override update to handle the optional avatar_url
    def update(
        self,
        db: Session,
        *,
        db_obj: models.Student, # Existing ORM object
        obj_in: Union[student_schemas.StudentUpdate, Dict[str, Any]], # Update data
        avatar_url: Optional[str] = None # Explicitly accept avatar_url
    ) -> models.Student:
        """
        Updates an existing student record, handling the optional avatar_url update.

        Args:
            db: The SQLAlchemy database session.
            db_obj: The existing Student ORM object.
            obj_in: Pydantic schema or dict with update data.
            avatar_url: The new avatar URL, if provided.

        Returns:
            The updated Student ORM object.
        """
        # Use the base class update method first to handle standard fields
        # Note: The base update doesn't know about avatar_url directly
        updated_obj = super().update(db=db, db_obj=db_obj, obj_in=obj_in)

        # Now, specifically handle the avatar_url if it needs updating
        # Check if avatar_url was provided OR if 'avatar' field was present in the input schema
        # (indicating an intent to update, even if setting to None)
        needs_avatar_update = False
        if avatar_url is not None:
             needs_avatar_update = True
        elif isinstance(obj_in, student_schemas.StudentUpdate):
             # Check if 'avatar' field itself was part of the PATCH request data implicitly
             # This check might need refinement based on how File uploads are handled in the endpoint
             # A simpler check might be just `if avatar_url is not None:` if you only update
             # the URL when a new file is successfully uploaded.
             # Let's assume for now we only update if avatar_url is explicitly passed.
             # If you want to allow *removing* an avatar via PATCH without a new file,
             # you'd need a different signal, maybe a specific field in StudentUpdate schema.
             pass # Refine this logic if needed based on avatar handling

        if needs_avatar_update and updated_obj.avatar_url != avatar_url:
            updated_obj.avatar_url = avatar_url
            db.add(updated_obj) # Mark as dirty again if URL changed
            db.commit()       # Commit the change
            db.refresh(updated_obj) # Refresh to get final state

        return updated_obj

    # get() and remove() methods are inherited directly from CRUDBase
    # as their default implementation is likely sufficient.


# Create a single instance of CRUDStudent for the Student model.
# This instance will be imported and used by the API endpoints.
crud_student = CRUDStudent(models.Student)


