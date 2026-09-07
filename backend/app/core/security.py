from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fernet key for symmetric encryption (station passwords, etc.)
# In production, use a persistent key from environment variable
ENCRYPTION_KEY = settings.ENCRYPTION_KEY.encode() if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY else Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


def encrypt_station_password(password: str) -> str:
    """Encrypt station password using Fernet symmetric encryption."""
    return cipher_suite.encrypt(password.encode()).decode()


def decrypt_station_password(encrypted_password: str) -> str:
    """Decrypt station password."""
    return cipher_suite.decrypt(encrypted_password.encode()).decode()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
