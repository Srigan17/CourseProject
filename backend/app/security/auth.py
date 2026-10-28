import os
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import jwt
from pydantic import BaseModel
from backend.app.config import settings

class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int

class User(BaseModel):
    username: str
    role: str  # "ADMIN", "COORDINATOR", "CLIENT"
    client_id: Optional[str] = None
    hashed_password: str
    salt: str

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if not salt:
        salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()
    return pwd_hash, salt

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    expected_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(expected_hash, hashed_password)

# Simulated in-memory persistent credential store
USERS_DB: Dict[str, User] = {}

def init_default_users():
    if not USERS_DB:
        admin_hash, admin_salt = hash_password("Admin@Healthcare2026")
        coord_hash, coord_salt = hash_password("Coord@Federation2026")
        c1_hash, c1_salt = hash_password("Client1@HospitalA")
        c2_hash, c2_salt = hash_password("Client2@HospitalB")
        c3_hash, c3_salt = hash_password("Client3@HospitalC")
        
        USERS_DB["admin"] = User(username="admin", role="ADMIN", hashed_password=admin_hash, salt=admin_salt)
        USERS_DB["coordinator"] = User(username="coordinator", role="COORDINATOR", hashed_password=coord_hash, salt=coord_salt)
        USERS_DB["hospital_a"] = User(username="hospital_a", role="CLIENT", client_id="hospital_a", hashed_password=c1_hash, salt=c1_salt)
        USERS_DB["hospital_b"] = User(username="hospital_b", role="CLIENT", client_id="hospital_b", hashed_password=c2_hash, salt=c2_salt)
        USERS_DB["hospital_c"] = User(username="hospital_c", role="CLIENT", client_id="hospital_c", hashed_password=c3_hash, salt=c3_salt)

init_default_users()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return TokenPayload(**payload)
    except (jwt.PyJWTError, Exception):
        return None
