"""
Account model for bank accounts connected via Plaid API.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base


class Account(Base):
    """Bank account model for Plaid-connected accounts."""
    
    __tablename__ = "accounts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Plaid account information
    plaid_account_id = Column(String(255), unique=True, nullable=False, index=True)
    institution_id = Column(String(255), nullable=True)
    institution_name = Column(String(255), nullable=True)
    
    # Account details
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)  # checking, savings, credit, etc.
    account_subtype = Column(String(50), nullable=True)
    official_name = Column(String(255), nullable=True)
    
    # Account balance
    current_balance = Column(Numeric(15, 2), nullable=True)
    available_balance = Column(Numeric(15, 2), nullable=True)
    credit_limit = Column(Numeric(15, 2), nullable=True)
    
    # Account metadata
    mask = Column(String(10), nullable=True)  # Last 4 digits
    currency_code = Column(String(3), default="USD")
    
    # Status and settings
    is_active = Column(Boolean, default=True)
    sync_enabled = Column(Boolean, default=True)
    last_sync = Column(DateTime, nullable=True)
    
    # Additional metadata from Plaid
    plaid_metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Account(id={self.id}, name={self.account_name}, type={self.account_type})>"
    
    @property
    def display_name(self):
        """Get display-friendly account name."""
        if self.official_name:
            return self.official_name
        if self.mask:
            return f"{self.account_name} (...{self.mask})"
        return self.account_name
    
    @property
    def balance_display(self):
        """Get formatted balance for display."""
        if self.current_balance is not None:
            return f"${self.current_balance:,.2f}"
        return "N/A" 