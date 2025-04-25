# backend/app/db/crud/base.py
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

# Import the Base class from models (used for type hinting the ModelType)
# Ensure this path is correct relative to your project structure
from app.db.models.base import Base

# Define Type Variables for Generic CRUD operations
# ModelType will represent the SQLAlchemy model (e.g., models.Student)
ModelType = TypeVar("ModelType", bound=Base)
# CreateSchemaType will represent the Pydantic schema for creation (e.g., schemas.StudentCreate)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
# UpdateSchemaType will represent the Pydantic schema for updates (e.g., schemas.StudentUpdate)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic Base class for CRUD (Create, Read, Update, Delete) operations.

    Parameters:
        model: A SQLAlchemy model class (e.g., models.Student)
    """
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        Args:
            model: A SQLAlchemy model class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get a single record by its primary key ID.

        Args:
            db: The SQLAlchemy database session.
            id: The primary key ID of the record to retrieve.

        Returns:
            The ORM model instance if found, otherwise None.
        """
        # Construct a select statement for the specific model by ID
        stmt = select(self.model).where(self.model.id == id)
        # Execute the statement and fetch one result or None
        result = db.execute(stmt).scalar_one_or_none()
        return result

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.

        Args:
            db: The SQLAlchemy database session.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            A list of ORM model instances.
        """
        # Construct a select statement, order by ID, apply offset and limit
        stmt = select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        # Execute and fetch all scalar results
        results = db.execute(stmt).scalars().all()
        return results

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record in the database.

        Args:
            db: The SQLAlchemy database session.
            obj_in: The Pydantic schema containing the data for the new record.

        Returns:
            The newly created ORM model instance.
        """
        # Convert the Pydantic schema to a dictionary
        # Pydantic V2 uses model_dump(), V1 used dict()
        obj_in_data = obj_in.model_dump()
        # Create a new instance of the SQLAlchemy model
        db_obj = self.model(**obj_in_data)
        # Add the new object to the session
        db.add(db_obj)
        # Commit the transaction to save the record
        db.commit()
        # Refresh the object to get any database-generated values (like ID)
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType, # The existing ORM object fetched from the DB
        obj_in: Union[UpdateSchemaType, Dict[str, Any]] # Data for update (Schema or dict)
    ) -> ModelType:
        """
        Update an existing record in the database.

        Args:
            db: The SQLAlchemy database session.
            db_obj: The existing ORM model instance to update.
            obj_in: A Pydantic schema or dictionary containing the fields to update.

        Returns:
            The updated ORM model instance.
        """
        # Get the current data of the existing object as a dictionary
        obj_data = jsonable_encoder(db_obj)
        # Determine the source of update data (dict or Pydantic schema)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # For Pydantic schema, get only fields that were explicitly set
            # Pydantic V2 uses model_dump(exclude_unset=True), V1 used dict(exclude_unset=True)
            update_data = obj_in.model_dump(exclude_unset=True)

        # Iterate through the fields of the existing object's data
        for field in obj_data:
            # If the field exists in the update data, update the attribute
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        # Add the modified object to the session (marks it as dirty)
        db.add(db_obj)
        # Commit the transaction to save changes
        db.commit()
        # Refresh the object to reflect the update
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """
        Remove a record from the database by its primary key ID.

        Args:
            db: The SQLAlchemy database session.
            id: The primary key ID of the record to remove.

        Returns:
            The removed ORM model instance if found and deleted, otherwise None.
        """
        # Retrieve the object first to ensure it exists
        obj = self.get(db=db, id=id)
        if obj:
            # Delete the object from the session
            db.delete(obj)
            # Commit the transaction to remove from the database
            db.commit()
        return obj


