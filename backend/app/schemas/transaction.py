"""
Pydantic schemas for transactions, accounts, and budgets.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, validator
from uuid import UUID


class AccountBase(BaseModel):
    """Base account schema."""
    account_name: str
    account_type: str
    account_subtype: Optional[str] = None
    official_name: Optional[str] = None


class AccountResponse(AccountBase):
    """Schema for account response data."""
    id: UUID
    plaid_account_id: str
    institution_name: Optional[str] = None
    current_balance: Optional[Decimal] = None
    available_balance: Optional[Decimal] = None
    mask: Optional[str] = None
    currency_code: str = "USD"
    is_active: bool = True
    last_sync: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    """Base transaction schema."""
    amount: Decimal
    name: str
    merchant_name: Optional[str] = None
    date: date
    custom_category: Optional[str] = None
    subcategory: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class TransactionCreate(TransactionBase):
    """Schema for creating manual transactions."""
    account_id: UUID
    transaction_type: str = "debit"  # debit or credit
    
    @validator("amount")
    def validate_amount(cls, v):
        """Ensure amount is positive."""
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class TransactionUpdate(BaseModel):
    """Schema for updating transactions."""
    custom_category: Optional[str] = None
    subcategory: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    is_recurring: Optional[bool] = None


class TransactionResponse(TransactionBase):
    """Schema for transaction response data."""
    id: UUID
    account_id: UUID
    plaid_transaction_id: Optional[str] = None
    category: Optional[List[str]] = None
    transaction_type: str
    pending: bool = False
    location: Optional[Dict[str, Any]] = None
    is_recurring: bool = False
    confidence_score: Optional[Decimal] = None
    is_anomaly: bool = False
    anomaly_score: Optional[Decimal] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionFilter(BaseModel):
    """Schema for filtering transactions."""
    account_ids: Optional[List[UUID]] = None
    categories: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    transaction_type: Optional[str] = None  # debit, credit
    search_term: Optional[str] = None
    is_recurring: Optional[bool] = None
    is_anomaly: Optional[bool] = None


class TransactionSummary(BaseModel):
    """Schema for transaction summary data."""
    total_income: Decimal = 0
    total_expenses: Decimal = 0
    net_amount: Decimal = 0
    transaction_count: int = 0
    top_categories: List[Dict[str, Any]] = []
    daily_totals: List[Dict[str, Any]] = []


class BudgetBase(BaseModel):
    """Base budget schema."""
    name: str
    category: str
    budget_limit: Decimal
    period_type: str  # monthly, weekly, yearly
    start_date: date
    end_date: date
    alert_threshold: Decimal = 0.8
    auto_rollover: bool = False
    
    @validator("budget_limit")
    def validate_budget_limit(cls, v):
        """Ensure budget limit is positive."""
        if v <= 0:
            raise ValueError("Budget limit must be positive")
        return v
    
    @validator("alert_threshold")
    def validate_alert_threshold(cls, v):
        """Ensure alert threshold is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Alert threshold must be between 0 and 1")
        return v


class BudgetCreate(BudgetBase):
    """Schema for creating budgets."""
    pass


class BudgetUpdate(BaseModel):
    """Schema for updating budgets."""
    name: Optional[str] = None
    budget_limit: Optional[Decimal] = None
    alert_threshold: Optional[Decimal] = None
    auto_rollover: Optional[bool] = None
    is_active: Optional[bool] = None


class BudgetResponse(BudgetBase):
    """Schema for budget response data."""
    id: UUID
    spent_amount: Decimal = 0
    remaining_amount: Decimal
    utilization_percentage: float
    is_over_budget: bool
    should_alert: bool
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class SpendingInsight(BaseModel):
    """Schema for AI-generated spending insights."""
    insight_type: str  # trend, anomaly, recommendation
    title: str
    description: str
    category: Optional[str] = None
    confidence_score: float
    created_at: datetime


class ForecastData(BaseModel):
    """Schema for spending forecast data."""
    category: str
    forecast_amount: Decimal
    confidence_interval_lower: Decimal
    confidence_interval_upper: Decimal
    forecast_date: date
    trend: str  # increasing, decreasing, stable


class DashboardData(BaseModel):
    """Schema for dashboard summary data."""
    total_balance: Decimal
    monthly_income: Decimal
    monthly_expenses: Decimal
    monthly_savings: Decimal
    account_summary: List[AccountResponse]
    recent_transactions: List[TransactionResponse]
    spending_by_category: List[Dict[str, Any]]
    budget_status: List[BudgetResponse]
    spending_insights: List[SpendingInsight]
    forecasts: List[ForecastData]

    class Config:
        # Convert snake_case to camelCase for JSON output
        alias_generator = lambda field_name: ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(field_name.split('_')))
        allow_population_by_field_name = True 