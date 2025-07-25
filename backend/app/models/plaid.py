from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.session import Base

# Stores Plaid items for each user
class PlaidItem(Base):
    __tablename__ = "plaid_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)  # Add foreign key constraint
    access_token = Column(String, unique=True)
    item_id = Column(String, unique=True)
