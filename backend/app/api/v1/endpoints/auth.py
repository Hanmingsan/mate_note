# backend/app/api/v1/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # FastAPI security utils
from sqlalchemy.orm import Session
from typing import Annotated # For Depends with Form

from app.db import crud, models, session
from app.schemas import token as token_schemas
from app.schemas import user as user_schemas
from app.core.security import verify_password, create_access_token, decode_access_token
from app.core.config import settings

router = APIRouter()

# OAuth2PasswordBearer dependency: points to the token URL
# This tells FastAPI how clients should send the token (Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

# --- Dependency to get current user ---
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(session.get_db)
) -> models.User:
    """
    Dependency to get the current user based on the provided token.
    Raises HTTPException if the token is invalid or the user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = decode_access_token(token)
    if username is None:
        raise credentials_exception
    user = crud.crud_user.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)]
) -> models.User:
    """
    Dependency to get the current *active* user.
    Raises HTTPException if the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def get_current_active_superuser(
    current_user: Annotated[models.User, Depends(get_current_active_user)]
) -> models.User:
    """
    Dependency to get the current *active superuser*.
    Raises HTTPException if the user is not a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


# --- Authentication Endpoints ---

@router.post(
    "/token",
    response_model=token_schemas.Token,
    summary="Login for Access Token",
    tags=["Authentication"]
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], # Use FastAPI's form helper
    db: Session = Depends(session.get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Takes username and password from form data.
    """
    user = crud.crud_user.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    # Generate access token (you can customize expiry)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) # Read expiry from settings
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=user_schemas.User,
    summary="Get Current User",
    tags=["Authentication"]
)
async def read_users_me(
    current_user: Annotated[models.User, Depends(get_current_active_user)] # Use the dependency
):
    """
    Fetch the profile of the currently authenticated user.
    """
    return current_user

# --- (Optional) User Signup Endpoint ---
# You might want a separate endpoint for user creation/signup
@router.post(
    "/signup",
    response_model=user_schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Create New User",
    tags=["Authentication"],
    responses={400: {"description": "Username or email already exists"}}
)
def create_new_user(
    *,
    db: Session = Depends(session.get_db),
    user_in: user_schemas.UserCreate # Expect JSON body for signup
):
    """
    Create a new user account.
    """
    # Check if user already exists
    existing_user = crud.crud_user.get_user_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered.",
        )
    if user_in.email:
        existing_email = crud.crud_user.get_user_by_email(db, email=user_in.email)
        if existing_email:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered.",
            )
    # Create user
    user = crud.crud_user.create_user(db=db, user=user_in)
    return user

