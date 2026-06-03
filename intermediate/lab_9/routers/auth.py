from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from intermediate.lab_8.models import User
from intermediate.lab_9.auth import (
    LoginRequest,
    TokenResponse,
    create_token,
    hash_password,
    verify_password,
)
from intermediate.lab_9.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: LoginRequest, db: Session = Depends(get_db)):
    """Registra un nuevo usuario."""
    # Verificar que no exista
    existing = db.scalars(
        select(User).where(User.email == data.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email ya registrado",
        )

    user = User(
        name=data.email.split("@")[0],
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id, user.email)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Inicia sesión y devuelve un token JWT."""
    user = db.scalars(
        select(User).where(User.email == data.email)
    ).first()

    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    token = create_token(user.id, user.email)
    return TokenResponse(access_token=token)