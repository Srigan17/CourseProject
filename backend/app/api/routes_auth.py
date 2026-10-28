from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.app.security.auth import USERS_DB, verify_password, create_access_token, decode_access_token, hash_password, User
from backend.app.security.audit import audit_logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "CLIENT"
    client_id: Optional[str] = None

@router.post("/login")
def login(req: LoginRequest) -> Dict[str, Any]:
    user = USERS_DB.get(req.username)
    if not user or not verify_password(req.password, user.hashed_password, user.salt):
        audit_logger.log_event(
            event_type="AUTH_FAILURE",
            severity="WARNING",
            actor=req.username,
            details={"reason": "Invalid credentials provided"}
        )
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = create_access_token({"sub": user.username, "role": user.role, "client_id": user.client_id})
    audit_logger.log_event(
        event_type="AUTH_SUCCESS",
        severity="INFO",
        actor=user.username,
        client_id=user.client_id,
        details={"role": user.role}
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
        "client_id": user.client_id
    }

@router.post("/register")
def register(req: RegisterRequest) -> Dict[str, Any]:
    if req.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already exists.")
    pwd_hash, salt = hash_password(req.password)
    new_user = User(
        username=req.username,
        role=req.role.upper(),
        client_id=req.client_id or req.username,
        hashed_password=pwd_hash,
        salt=salt
    )
    USERS_DB[req.username] = new_user

    audit_logger.log_event(
        event_type="CLIENT_REGISTRATION",
        severity="INFO",
        actor="SYSTEM",
        client_id=new_user.client_id,
        details={"username": new_user.username, "role": new_user.role}
    )
    return {"message": "User registered successfully", "username": new_user.username, "role": new_user.role}

@router.get("/me")
def get_current_user(token: Optional[str] = None) -> Dict[str, Any]:
    if not token:
        # Default guest/demo user for dashboard
        return {"username": "admin", "role": "ADMIN", "client_id": None}
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return {"username": payload.sub, "role": payload.role}
