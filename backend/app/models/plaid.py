from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.session import Base

# Stores Plaid items for each user
class PlaidItem(Base):
    __tablename__ = "plaid_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Simplified — link to users
    access_token = Column(String, unique=True)
    item_id = Column(String, unique=True)
