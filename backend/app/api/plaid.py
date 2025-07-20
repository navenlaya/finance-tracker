# app/api/plaid.py

from fastapi import APIRouter, Depends, HTTPException, Query
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
    Fetch accounts for all Plaid items linked to the authenticated user.
    """
    items = db.query(PlaidItem).filter_by(user_id=current_user.id).all()
    if not items:
        raise HTTPException(status_code=404, detail="No Plaid account linked.")
    all_accounts = []
    for item in items:
        try:
            client = get_plaid_client()
            access_token = decrypt_token(item.access_token)
            response = client.accounts_get({"access_token": access_token})
            accounts = response.to_dict()["accounts"]
            for acct in accounts:
                acct["item_id"] = item.item_id  # Attach item_id for frontend
            all_accounts.extend(accounts)
        except Exception as e:
            continue  # Skip failed items
    return {"accounts": all_accounts}

@router.get("/transactions")
def get_transactions_endpoint(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Fetch recent transactions for all Plaid items linked to the authenticated user.
    """
    items = db.query(PlaidItem).filter_by(user_id=current_user.id).all()
    if not items:
        raise HTTPException(status_code=404, detail="No Plaid account linked.")
    all_transactions = []
    for item in items:
        try:
            txns_response = get_transactions(item.access_token)
            if txns_response and "transactions" in txns_response:
                all_transactions.extend(txns_response["transactions"])
        except Exception as e:
            continue  # Skip failed items
    return {"transactions": all_transactions}

@router.delete("/remove-account")
def remove_account(item_id: str = Query(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Remove a linked Plaid account (PlaidItem) by item_id for the authenticated user.
    """
    item = db.query(PlaidItem).filter_by(user_id=current_user.id, item_id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Plaid account not found.")
    db.delete(item)
    db.commit()
    return {"detail": "Plaid account removed."}
