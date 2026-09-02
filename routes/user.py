import logging

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from typing import Optional

from core.config import get_settings
from core.limiter import limiter
from database.config import user_collection
from model.user import User, UserCreate, UserInDB

settings = get_settings()
logger = logging.getLogger("portfolio.auth")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

password_hasher = PasswordHash.recommended()

# -------------------- PASSWORD UTILS --------------------

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return password_hasher.verify(plain, hashed)

# -------------------- AUTH CORE --------------------

def authenticate_user(username: str, password: str):
    user = user_collection.find_one({"username": username})
    if not user:
        return None
    if not user.get("hashed_password") or not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None):
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=15))
    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_collection.find_one({"username": username})
    if not user:
        raise credentials_exception

    user_in_db = UserInDB(**user)
    if user_in_db.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return user_in_db

# -------------------- ROUTES --------------------

@router.post(
    "/register",
    response_model=User,
    summary="Create the site owner's admin account (bootstrap only)",
    description=(
        "Only works while no user account exists yet. Once the first admin "
        "account has been created, this endpoint always returns 403 — there "
        "is no open/public registration."
    ),
)
@limiter.limit("5/minute")
async def register(request: Request, user: UserCreate):
    if user_collection.count_documents({}) > 0:
        logger.warning("Blocked registration attempt: an admin account already exists.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is closed. An admin account already exists.",
        )

    if len(user.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long.",
        )

    user_dict = {
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "role": "admin",
    }

    user_collection.insert_one(user_dict)
    logger.info("Bootstrap admin account created for username=%s", user.username)
    return User(username=user.username, role="admin")


@router.post("/login", summary="Log in and receive a bearer token")
@limiter.limit("10/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning("Failed login attempt for username=%s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user["username"],
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=User, summary="Return the currently authenticated user")
async def read_current_user(current_user: UserInDB = Depends(get_current_user)):
    return User(username=current_user.username, role=current_user.role)
