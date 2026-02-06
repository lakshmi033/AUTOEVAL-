# auth.py
"""
Authentication and authorization utilities for AutoEval+.

Features:
- Password hashing (bcrypt via passlib)
- JWT access token generation and validation
- FastAPI dependencies for:
  - get_current_user
  - get_current_admin (role-based access control)
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import TokenData

# -----------------------------------------------------------------------------
# Security configuration
# -----------------------------------------------------------------------------

# NOTE: For a real deployment, move SECRET_KEY to an environment variable.
SECRET_KEY = "CHANGE_THIS_SECRET_KEY_FOR_PRODUCTION_USE"  # <- replace in real deploy
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours for stability during testing

# OAuth2 scheme used to extract "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# -----------------------------------------------------------------------------
# Password hashing helpers
# -----------------------------------------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plaintext password matches a previously hashed password.
    """
    # Ensure password is bytes for bcrypt
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


# -----------------------------------------------------------------------------
# User helper functions
# -----------------------------------------------------------------------------

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str, required_role: Optional[str] = None) -> Optional[User]:
    """
    Verify user credentials AND role.
    Returns User if authentication is successful, otherwise None.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
        
    # Strict Role Check if specified
    if required_role and user.role != required_role:
        return None  # Role mismatch counts as failed auth
        
    if not verify_password(password, user.hashed_password):
        return None
    return user


# -----------------------------------------------------------------------------
# JWT helpers
# -----------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT containing the given data.

    Common claims used:
    - sub: subject identifier (here we use the user email)
    - role: user role ("admin" / "user")
    - exp: expiration timestamp
    """
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# -----------------------------------------------------------------------------
# FastAPI dependencies for auth
# -----------------------------------------------------------------------------

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and validate the current user from the JWT access token.

    - Decodes token
    - Fetches user from the database
    - Ensures the user exists and is active
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, role=role)
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, email=token_data.email)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Restrict access to admin users only.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required.",
        )
    return current_user
