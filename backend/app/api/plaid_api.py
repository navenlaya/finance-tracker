"""
Plaid API endpoints for bank account connection and data synchronization.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.session import get_db
from app.api.auth import get_current_active_user
from app.models.user import User
from app.schemas.user import PlaidConnection
from app.schemas.transaction import AccountResponse, TransactionResponse
from app.services.plaid import plaid_service
from app.core.security import encrypt_plaid_token, decrypt_plaid_token

router = APIRouter()


class LinkTokenRequest(BaseModel):
    """Schema for link token request."""
    pass


class LinkTokenResponse(BaseModel):
    """Schema for link token response."""
    link_token: str


class PublicTokenExchange(BaseModel):
    """Schema for public token exchange."""
    public_token: str
    institution_id: str
    institution_name: str


class SyncRequest(BaseModel):
    """Schema for manual sync request."""
    days_back: int = 30


@router.post("/create-link-token", response_model=LinkTokenResponse)
async def create_link_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a Plaid Link token for account connection.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Link token for Plaid Link initialization
    """
    try:
        link_token = await plaid_service.create_link_token(
            user_id=str(current_user.id),
            user_email=current_user.email
        )
        
        return LinkTokenResponse(link_token=link_token)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create link token: {str(e)}"
        )


@router.post("/exchange-public-token")
async def exchange_public_token(
    token_data: PublicTokenExchange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Exchange public token for access token and connect user's bank account.
    
    Args:
        token_data: Public token exchange data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Success message and account information
    """
    try:
        # Exchange public token for access token
        access_token = await plaid_service.exchange_public_token(token_data.public_token)
        
        # Encrypt and store access token
        encrypted_token = encrypt_plaid_token(access_token)
        current_user.plaid_access_token = encrypted_token
        
        # Store institution information
        # Note: In a real app, you might want to create an Institution model
        # For now, we'll store basic info in user metadata
        
        await db.commit()
        
        # Sync accounts immediately after connection
        decrypted_token = decrypt_plaid_token(encrypted_token)
        accounts = await plaid_service.sync_user_accounts(db, current_user, decrypted_token)
        
        return {
            "message": "Bank account connected successfully",
            "institution_name": token_data.institution_name,
            "accounts_connected": len(accounts)
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect bank account: {str(e)}"
        )


@router.get("/connection-status", response_model=PlaidConnection)
async def get_connection_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's Plaid connection status.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Plaid connection status information
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Connection status request for user_id: {current_user.id}")
        logger.info(f"User has plaid_access_token: {bool(current_user.plaid_access_token)}")
        
        is_connected = bool(current_user.plaid_access_token)
        
        if is_connected:
            # Get account count and last sync info
            from sqlalchemy.future import select
            from sqlalchemy import func
            from app.models.account import Account
            
            result = await db.execute(
                select(func.count(Account.id)).where(Account.user_id == current_user.id)
            )
            accounts_count = result.scalar() or 0
            
            logger.info(f"Found {accounts_count} accounts for user")
            
            # Get most recent sync time
            sync_result = await db.execute(
                select(func.max(Account.last_sync)).where(Account.user_id == current_user.id)
            )
            last_sync = sync_result.scalar()
            
            logger.info(f"Connection status returning: is_connected=True, accounts_count={accounts_count}")
            
            return PlaidConnection(
                isConnected=True,
                accountsCount=accounts_count,
                lastSync=last_sync
            )
        else:
            logger.info(f"Connection status returning: is_connected=False")
            return PlaidConnection(
                isConnected=False,
                accountsCount=0
            )
            
    except Exception as e:
        logger.error(f"Error in connection status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get connection status: {str(e)}"
        )


@router.post("/sync-accounts")
async def sync_accounts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually sync user's bank accounts.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Sync results
    """
    if not current_user.plaid_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Plaid connection found. Please connect your bank account first."
        )
    
    try:
        access_token = decrypt_plaid_token(current_user.plaid_access_token)
        accounts = await plaid_service.sync_user_accounts(db, current_user, access_token)
        
        return {
            "message": "Accounts synced successfully",
            "accounts_synced": len(accounts),
            "sync_time": accounts[0].last_sync if accounts else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync accounts: {str(e)}"
        )


@router.post("/sync-transactions")
async def sync_transactions(
    sync_data: SyncRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually sync user's transactions.
    
    Args:
        sync_data: Sync configuration
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Sync results
    """
    if not current_user.plaid_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Plaid connection found. Please connect your bank account first."
        )
    
    try:
        access_token = decrypt_plaid_token(current_user.plaid_access_token)
        transactions = await plaid_service.sync_user_transactions(
            db, current_user, access_token, sync_data.days_back
        )
        
        return {
            "message": "Transactions synced successfully",
            "transactions_synced": len(transactions),
            "days_back": sync_data.days_back
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync transactions: {str(e)}"
        )


@router.delete("/disconnect")
async def disconnect_plaid(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disconnect user's Plaid connection.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Success message
    """
    try:
        # Remove Plaid access token
        current_user.plaid_access_token = None
        current_user.plaid_item_id = None
        
        # Optionally, you might want to deactivate accounts instead of keeping them
        # For now, we'll keep the accounts and transactions for historical data
        
        await db.commit()
        
        return {"message": "Plaid connection disconnected successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect Plaid: {str(e)}"
        )


@router.post("/webhook")
async def plaid_webhook(webhook_data: Dict[str, Any]):
    """
    Handle Plaid webhook notifications.
    
    Args:
        webhook_data: Webhook payload from Plaid
    
    Returns:
        Acknowledgment
    """
    # This is a simplified webhook handler
    # In production, you should verify the webhook signature
    # and handle different webhook types appropriately
    
    webhook_type = webhook_data.get('webhook_type')
    webhook_code = webhook_data.get('webhook_code')
    
    # Log webhook for monitoring
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Received Plaid webhook: {webhook_type}.{webhook_code}")
    
    # Handle different webhook types
    if webhook_type == 'TRANSACTIONS':
        if webhook_code == 'INITIAL_UPDATE':
            # Handle initial transaction data availability
            pass
        elif webhook_code == 'HISTORICAL_UPDATE':
            # Handle historical transaction data availability
            pass
        elif webhook_code == 'DEFAULT_UPDATE':
            # Handle new transaction data
            pass
    elif webhook_type == 'ITEM':
        if webhook_code == 'ERROR':
            # Handle item errors
            pass
    
    return {"acknowledged": True} 