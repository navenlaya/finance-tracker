"""
Transaction management API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc
from datetime import date, datetime, timedelta
from app.db.session import get_db
from app.api.auth import get_current_active_user
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionResponse,
    TransactionCreate,
    TransactionUpdate,
    TransactionSummary,
    DashboardData
)

router = APIRouter()


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, le=1000),
    offset: int = Query(0, ge=0),
    account_id: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get transactions for the current user with filtering options."""
    query = select(Transaction).where(Transaction.user_id == current_user.id)
    
    if account_id:
        query = query.where(Transaction.account_id == account_id)
    if category:
        query = query.where(Transaction.custom_category == category)
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    
    query = query.order_by(desc(Transaction.date)).limit(limit).offset(offset)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return [TransactionResponse.from_orm(transaction) for transaction in transactions]


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard summary data."""
    # This is a placeholder implementation
    # In a real application, you would calculate actual statistics
    
    return DashboardData(
        total_balance=0,
        monthly_income=0,
        monthly_expenses=0,
        monthly_savings=0,
        account_summary=[],
        recent_transactions=[],
        spending_by_category=[],
        budget_status=[],
        spending_insights=[],
        forecasts=[]
    )


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a manual transaction."""
    new_transaction = Transaction(
        user_id=current_user.id,
        account_id=transaction_data.account_id,
        amount=transaction_data.amount,
        name=transaction_data.name,
        merchant_name=transaction_data.merchant_name,
        date=transaction_data.date,
        custom_category=transaction_data.custom_category,
        subcategory=transaction_data.subcategory,
        notes=transaction_data.notes,
        tags=transaction_data.tags,
        transaction_type=transaction_data.transaction_type,
        iso_currency_code="USD"
    )
    
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)
    
    return TransactionResponse.from_orm(new_transaction)


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a transaction."""
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    for field, value in transaction_update.dict(exclude_unset=True).items():
        setattr(transaction, field, value)
    
    await db.commit()
    await db.refresh(transaction)
    
    return TransactionResponse.from_orm(transaction) 