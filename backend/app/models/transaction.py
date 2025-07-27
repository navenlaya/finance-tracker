"""
Transaction model for financial transactions from Plaid API.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Text, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from app.db.session import Base


class Transaction(Base):
    """Financial transaction model for Plaid transactions."""
    
    __tablename__ = "transactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    
    # Plaid transaction information
    plaid_transaction_id = Column(String(255), unique=True, nullable=False, index=True)
    plaid_account_id = Column(String(255), nullable=False)
    
    # Transaction details
    amount = Column(Numeric(15, 2), nullable=False)  # Always positive
    iso_currency_code = Column(String(3), default="USD")
    name = Column(String(500), nullable=False)  # Merchant/description
    merchant_name = Column(String(255), nullable=True)
    
    # Transaction dates
    date = Column(Date, nullable=False, index=True)
    authorized_date = Column(Date, nullable=True)
    
    # Categorization (from Plaid)
    category = Column(ARRAY(String), nullable=True)  # Plaid category hierarchy
    category_id = Column(String(50), nullable=True)
    
    # Enhanced categorization (our custom categories)
    custom_category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    
    # Transaction type and status
    transaction_type = Column(String(50), nullable=False)  # debit, credit, etc.
    pending = Column(Boolean, default=False)
    
    # Location information
    location = Column(JSONB, nullable=True)  # Store address, coordinates, etc.
    
    # User annotations
    notes = Column(Text, nullable=True)
    is_recurring = Column(Boolean, default=False)
    confidence_score = Column(Numeric(3, 2), nullable=True)  # ML confidence for categorization
    
    # Fraud/anomaly detection
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Numeric(5, 4), nullable=True)
    anomaly_reason = Column(String(255), nullable=True)
    
    # Additional Plaid metadata
    plaid_metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, name={self.name})>"
    
    @property
    def amount_display(self):
        """Get formatted amount for display."""
        return f"${self.amount:,.2f}"
    
    @property
    def primary_category(self):
        """Get the primary category for display."""
        if self.custom_category:
            return self.custom_category
        elif self.category and len(self.category) > 0:
            return self.category[0]
        return "Uncategorized"
    
    @property
    def is_expense(self):
        """Check if transaction is an expense (debit)."""
        return self.transaction_type == "debit"
    
    @property
    def is_income(self):
        """Check if transaction is income (credit)."""
        return self.transaction_type == "credit"


class Budget(Base):
    """Budget model for user spending goals and limits."""
    
    __tablename__ = "budgets"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Budget details
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    budget_limit = Column(Numeric(15, 2), nullable=False)
    spent_amount = Column(Numeric(15, 2), default=0)
    
    # Time period
    period_type = Column(String(20), nullable=False)  # monthly, weekly, yearly
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Settings
    alert_threshold = Column(Numeric(3, 2), default=0.8)  # Alert at 80% of budget
    is_active = Column(Boolean, default=True)
    auto_rollover = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="budgets")
    
    def __repr__(self):
        return f"<Budget(id={self.id}, name={self.name}, limit={self.budget_limit})>"
    
    @property
    def remaining_amount(self):
        """Get remaining budget amount."""
        return max(0, self.budget_limit - self.spent_amount)
    
    @property
    def utilization_percentage(self):
        """Get budget utilization as percentage."""
        if self.budget_limit > 0:
            return min(100, (self.spent_amount / self.budget_limit) * 100)
        return 0
    
    @property
    def is_over_budget(self):
        """Check if budget is exceeded."""
        return self.spent_amount > self.budget_limit
    
    @property
    def should_alert(self):
        """Check if user should be alerted about budget usage."""
        return self.utilization_percentage >= (self.alert_threshold * 100) 