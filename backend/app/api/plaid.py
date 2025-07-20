# app/api/plaid.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.plaid import LinkTokenResponse, PublicTokenRequest, TokenExchangeResponse
from app.services.plaid import create_link_token, exchange_public_token, get_transactions
from app.models.plaid import PlaidItem
from app.core.security import get_current_user
from app.models.user import User
from app.core.security import get_db
from app.services.plaid import get_plaid_client, decrypt_token

router = APIRouter()

@router.get("/link-token", response_model=LinkTokenResponse)
def get_link_token(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> LinkTokenResponse:
    """
    Generate a Plaid Link token for the authenticated user.
    """
    token = create_link_token(user_id=str(current_user.id))
    return LinkTokenResponse(link_token=token["link_token"])

@router.post("/exchange", response_model=TokenExchangeResponse)
def exchange_token(payload: PublicTokenRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TokenExchangeResponse:
    """
    Exchange a Plaid public token for an access token and store it for the authenticated user.
    """
    try:
        token_data = exchange_public_token(payload.public_token)
        item = PlaidItem(
            user_id=current_user.id,
            access_token=token_data["access_token"],
            item_id=token_data["item_id"]
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return TokenExchangeResponse(
            access_token=token_data["access_token"],
            item_id=token_data["item_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/accounts")
def get_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Fetch accounts for the authenticated user from Plaid.
    """
    item = db.query(PlaidItem).filter_by(user_id=current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No Plaid account linked.")
    # Fetch accounts from Plaid
    try:
        client = get_plaid_client()
        access_token = decrypt_token(item.access_token)
        response = client.accounts_get({"access_token": access_token})
        return {"accounts": response.to_dict()["accounts"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions")
def get_transactions_endpoint(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Fetch recent transactions for the authenticated user from Plaid.
    """
    item = db.query(PlaidItem).filter_by(user_id=current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No Plaid account linked.")
    try:
        transactions = get_transactions(item.access_token)
        return {"transactions": transactions["transactions"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
