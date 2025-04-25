# backend/app/db/models/__init__.py

# Import the Base class from base.py so it's accessible
# directly from app.db.models
from .base import Base

# Import all the models defined in this directory.
# This ensures they are registered with Base.metadata when this package is imported.
# It also makes them available for import directly from app.db.models.
from .student import Student

# If you add more models (e.g., Course, Enrollment), import them here as well:
# from .course import Course
# from .enrollment import Enrollment


