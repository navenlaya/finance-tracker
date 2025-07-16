# app/api/plaid.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.plaid import LinkTokenResponse, PublicTokenRequest, TokenExchangeResponse
from app.services.plaid import create_link_token, exchange_public_token
from app.models.plaid import PlaidItem
from app.db.session import Base
from app.schemas.user import UserOut

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ⚡ (Later) Protect this route with JWT and inject user_id from token
@router.get("/link-token", response_model=LinkTokenResponse)
def get_link_token(db: Session = Depends(get_db)):
    # For now, mock user ID = "123"; in reality, this comes from token
    token = create_link_token(user_id="123")
    return {"link_token": token["link_token"]}

@router.post("/exchange", response_model=TokenExchangeResponse)
def exchange_token(payload: PublicTokenRequest, db: Session = Depends(get_db)):
    try:
        token_data = exchange_public_token(payload.public_token)
        item = PlaidItem(
            user_id=123,  # Replace with real user from JWT
            access_token=token_data["access_token"],
            item_id=token_data["item_id"]
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return {
            "access_token": token_data["access_token"],
            "item_id": token_data["item_id"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
