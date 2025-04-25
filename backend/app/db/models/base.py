# backend/app/db/models/base.py

from sqlalchemy.orm import declarative_base

# Create the shared Declarative Base for all models
Base = declarative_base()

# Optional: You can import all your models here.
# This can sometimes help ensure they are registered with Base.metadata,
# especially for tools like Alembic or when initializing the database.
# However, ensure there are no circular import issues.
# Example:
# from .student import Student # noqa (noqa prevents linting errors if unused directly here)
# ... import other models ...


