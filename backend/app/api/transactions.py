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


@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard summary data."""
    from app.models.account import Account
    from decimal import Decimal
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"Dashboard request for user_id: {current_user.id}")
    
    # Get all user accounts
    account_result = await db.execute(
        select(Account).where(Account.user_id == current_user.id)
    )
    accounts = account_result.scalars().all()
    
    logger.info(f"Found {len(accounts)} accounts for user")
    
    # Calculate total balance and create account summary
    total_balance = Decimal('0')
    account_summary = []
    
    for account in accounts:
        balance = account.current_balance or Decimal('0')
        total_balance += balance
        logger.info(f"Account {account.account_name}: balance={balance}")
        account_summary.append({
            "id": str(account.id),
            "name": account.account_name,
            "type": account.account_type,
            "balance": str(balance),
            "last_updated": account.last_sync.isoformat() if account.last_sync else None
        })
    
    logger.info(f"Total balance calculated: {total_balance}")
    
    # Get recent transactions (last 10)
    recent_transactions_result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(desc(Transaction.date))
        .limit(10)
    )
    recent_transactions_data = recent_transactions_result.scalars().all()
    
    recent_transactions = []
    for txn in recent_transactions_data:
        recent_transactions.append({
            "id": str(txn.id),
            "description": txn.name,  # Transaction model uses 'name' field
            "amount": str(txn.amount),
            "date": txn.date.isoformat(),
            "category": txn.custom_category or "Uncategorized"
        })
    
    # Calculate monthly stats (simplified - last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    monthly_transactions = await db.execute(
        select(Transaction)
        .where(
            and_(
                Transaction.user_id == current_user.id,
                Transaction.date >= thirty_days_ago
            )
        )
    )
    monthly_txns = monthly_transactions.scalars().all()
    
    monthly_income = sum(txn.amount for txn in monthly_txns if txn.amount > 0)
    monthly_expenses = abs(sum(txn.amount for txn in monthly_txns if txn.amount < 0))
    monthly_savings = monthly_income - monthly_expenses
    
    # Return plain dictionary with camelCase keys for frontend compatibility
    return {
        "totalBalance": float(total_balance),
        "monthlyIncome": float(monthly_income),
        "monthlyExpenses": float(monthly_expenses),
        "monthlySavings": float(monthly_savings),
        "accountSummary": account_summary,
        "recentTransactions": recent_transactions,
        "spendingByCategory": [],  # TODO: Implement category breakdown
        "budgetStatus": [],  # TODO: Implement budget tracking
        "spendingInsights": [],  # TODO: Implement insights
        "forecasts": []  # TODO: Implement forecasting
    }


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