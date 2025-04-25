# backend/app/api/v1/api.py

from fastapi import APIRouter

# Import the router defined in the students endpoint file
from .endpoints import students
# If you add an auth endpoint file, import its router here as well
# from .endpoints import auth

# Create the main router for the v1 API
api_router_v1 = APIRouter()

# Include the students router with a specific prefix and tags
# All routes in students.router will now be prefixed with /students
# e.g., GET / becomes GET /students/
# e.g., GET /{student_id} becomes GET /students/{student_id}
api_router_v1.include_router(students.router, prefix="/students", tags=["Students"])

# Include other routers here if needed
# api_router_v1.include_router(auth.router, prefix="/auth", tags=["Authentication"])

