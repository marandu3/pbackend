from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pwdlib import PasswordHash
from dotenv import load_dotenv
from typing import Optional
import os

from database.config import user_collection
from model.user import User, UserCreate, UserInDB

load_dotenv()

SECRET_KEY = os.getenv("SECRETE_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

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
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    payload = {
        "sub": subject,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_collection.find_one({"username": username})
    if not user:
        raise credentials_exception

    return UserInDB(**user)

# -------------------- ROUTES --------------------

@router.post("/register", response_model=User)
async def register(user: UserCreate):
    if user_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    user_dict = {
        "username": user.username,
        "hashed_password": hash_password(user.password),
    }

    user_collection.insert_one(user_dict)
    return User(username=user.username)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user["username"],
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=User)
async def read_current_user(current_user: UserInDB = Depends(get_current_user)):
    return User(username=current_user.username)
