"""
Plaid service for bank account integration and transaction syncing.
Handles Plaid API interactions, account connections, and data synchronization.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import settings
from app.core.security import encrypt_plaid_token, decrypt_plaid_token
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)


class PlaidService:
    """Service for handling Plaid API interactions."""
    
    def __init__(self):
        """Initialize Plaid client with configuration."""
        configuration = Configuration(
            host=self._get_plaid_host(),
            api_key={
                'clientId': settings.plaid_client_id,
                'secret': settings.plaid_secret,
            }
        )
        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
        
    def _get_plaid_host(self):
        """Get Plaid host based on environment."""
        if settings.plaid_env == "sandbox":
            return plaid.Environment.Sandbox
        elif settings.plaid_env == "development":
            return plaid.Environment.Development
        else:
            return plaid.Environment.Production
    
    def _serialize_plaid_data(self, data):
        """Convert Plaid API objects to JSON-serializable dictionaries."""
        if hasattr(data, 'to_dict'):
            return data.to_dict()
        elif isinstance(data, dict):
            # Recursively serialize dictionary values
            serialized = {}
            for key, value in data.items():
                if hasattr(value, 'to_dict'):
                    serialized[key] = value.to_dict()
                elif hasattr(value, '__dict__'):
                    # Convert object to dict if it has attributes
                    serialized[key] = {k: v for k, v in value.__dict__.items() if not k.startswith('_')}
                else:
                    serialized[key] = value
            return serialized
        else:
            return data
    
    async def create_link_token(self, user_id: str, user_email: str) -> str:
        """
        Create a link token for Plaid Link initialization.
        
        Args:
            user_id: User ID
            user_email: User email
            
        Returns:
            Link token string
        """
        try:
            request = LinkTokenCreateRequest(
                products=[Products(prod) for prod in settings.plaid_products],
                client_name="Finance Tracker",
                country_codes=[CountryCode(code) for code in settings.plaid_country_codes],
                language='en',
                user=LinkTokenCreateRequestUser(client_user_id=user_id),
                webhook='https://your-webhook-url.com/plaid/webhook'  # Replace with actual webhook URL
            )
            
            response = self.client.link_token_create(request)
            return response['link_token']
            
        except Exception as e:
            logger.error(f"Error creating link token: {e}")
            raise Exception(f"Failed to create link token: {str(e)}")
    
    async def exchange_public_token(self, public_token: str) -> str:
        """
        Exchange public token for access token.
        
        Args:
            public_token: Public token from Plaid Link
            
        Returns:
            Access token
        """
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            return response['access_token']
            
        except Exception as e:
            logger.error(f"Error exchanging public token: {e}")
            raise Exception(f"Failed to exchange public token: {str(e)}")
    
    async def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Get account information from Plaid.
        
        Args:
            access_token: Plaid access token
            
        Returns:
            List of account data
        """
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)
            return response['accounts']
            
        except Exception as e:
            logger.error(f"Error getting accounts: {e}")
            raise Exception(f"Failed to get accounts: {str(e)}")
    
    async def get_transactions(
        self, 
        access_token: str, 
        start_date: date, 
        end_date: date,
        account_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get transactions from Plaid.
        
        Args:
            access_token: Plaid access token
            start_date: Start date for transactions
            end_date: End date for transactions
            account_ids: Optional list of specific account IDs
            
        Returns:
            List of transaction data
        """
        try:
            # Build request parameters
            request_params = {
                'access_token': access_token,
                'start_date': start_date,
                'end_date': end_date
            }
            
            # Only add account_ids if provided
            if account_ids is not None:
                request_params['account_ids'] = account_ids
            
            request = TransactionsGetRequest(**request_params)
            
            response = self.client.transactions_get(request)
            
            # Handle response safely
            if not response or 'transactions' not in response:
                logger.warning("No transactions returned from Plaid API")
                return []
            
            transactions = response['transactions']
            total_transactions = response.get('total_transactions', len(transactions))
            
            logger.info(f"Retrieved {len(transactions)} of {total_transactions} transactions")
            
            # Handle pagination if there are more transactions
            while len(transactions) < total_transactions:
                request.offset = len(transactions)
                response = self.client.transactions_get(request)
                
                if response and 'transactions' in response:
                    transactions.extend(response['transactions'])
                else:
                    logger.warning("Failed to get additional transactions during pagination")
                    break
            
            logger.info(f"Total transactions retrieved: {len(transactions)}")
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            logger.error(f"Request params: access_token={'***' if access_token else None}, start_date={start_date}, end_date={end_date}, account_ids={account_ids}")
            raise Exception(f"Failed to get transactions: {str(e)}")
    
    async def sync_user_accounts(self, db: AsyncSession, user: User, access_token: str) -> List[Account]:
        """
        Sync user accounts from Plaid to database.
        
        Args:
            db: Database session
            user: User object
            access_token: Plaid access token
            
        Returns:
            List of synced accounts
        """
        try:
            # Get accounts from Plaid
            plaid_accounts = await self.get_accounts(access_token)
            synced_accounts = []
            
            for plaid_account in plaid_accounts:
                # Check if account already exists
                result = await db.execute(
                    select(Account).where(Account.plaid_account_id == plaid_account['account_id'])
                )
                existing_account = result.scalar_one_or_none()
                
                if existing_account:
                    # Update existing account
                    existing_account.account_name = plaid_account['name']
                    existing_account.account_type = str(plaid_account['type'])
                    existing_account.account_subtype = str(plaid_account.get('subtype')) if plaid_account.get('subtype') else None
                    existing_account.official_name = plaid_account.get('official_name')
                    existing_account.mask = plaid_account.get('mask')
                    
                    # Update balances
                    balances = plaid_account.get('balances', {})
                    existing_account.current_balance = Decimal(str(balances.get('current', 0)))
                    existing_account.available_balance = Decimal(str(balances.get('available', 0)))
                    existing_account.credit_limit = Decimal(str(balances.get('limit', 0))) if balances.get('limit') else None
                    
                    existing_account.last_sync = datetime.utcnow()
                    # Convert plaid_account to a serializable dict
                    serializable_metadata = {
                        'account_id': plaid_account['account_id'],
                        'name': plaid_account['name'],
                        'type': str(plaid_account['type']),
                        'subtype': str(plaid_account.get('subtype')) if plaid_account.get('subtype') else None,
                        'official_name': plaid_account.get('official_name'),
                        'mask': plaid_account.get('mask'),
                        'balances': {
                            'current': balances.get('current'),
                            'available': balances.get('available'),
                            'limit': balances.get('limit'),
                            'iso_currency_code': balances.get('iso_currency_code')
                        }
                    }
                    existing_account.plaid_metadata = serializable_metadata
                    
                    synced_accounts.append(existing_account)
                    
                else:
                    # Create new account
                    balances = plaid_account.get('balances', {})
                    # Convert plaid_account to a serializable dict
                    serializable_metadata = {
                        'account_id': plaid_account['account_id'],
                        'name': plaid_account['name'],
                        'type': str(plaid_account['type']),
                        'subtype': str(plaid_account.get('subtype')) if plaid_account.get('subtype') else None,
                        'official_name': plaid_account.get('official_name'),
                        'mask': plaid_account.get('mask'),
                        'balances': {
                            'current': balances.get('current'),
                            'available': balances.get('available'),
                            'limit': balances.get('limit'),
                            'iso_currency_code': balances.get('iso_currency_code')
                        }
                    }
                    new_account = Account(
                        user_id=user.id,
                        plaid_account_id=plaid_account['account_id'],
                        account_name=plaid_account['name'],
                        account_type=str(plaid_account['type']),
                        account_subtype=str(plaid_account.get('subtype')) if plaid_account.get('subtype') else None,
                        official_name=plaid_account.get('official_name'),
                        current_balance=Decimal(str(balances.get('current', 0))),
                        available_balance=Decimal(str(balances.get('available', 0))),
                        credit_limit=Decimal(str(balances.get('limit', 0))) if balances.get('limit') else None,
                        mask=plaid_account.get('mask'),
                        currency_code=balances.get('iso_currency_code', 'USD'),
                        last_sync=datetime.utcnow(),
                        plaid_metadata=serializable_metadata
                    )
                    
                    db.add(new_account)
                    synced_accounts.append(new_account)
            
            await db.commit()
            return synced_accounts
            
        except Exception as e:
            logger.error(f"Error syncing accounts: {e}")
            await db.rollback()
            raise Exception(f"Failed to sync accounts: {str(e)}")
    
    async def sync_user_transactions(
        self, 
        db: AsyncSession, 
        user: User, 
        access_token: str,
        days_back: int = 30
    ) -> List[Transaction]:
        """
        Sync user transactions from Plaid to database.
        
        Args:
            db: Database session
            user: User object
            access_token: Plaid access token
            days_back: Number of days to sync back
            
        Returns:
            List of synced transactions
        """
        try:
            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            # Get transactions from Plaid
            plaid_transactions = await self.get_transactions(access_token, start_date, end_date)
            synced_transactions = []
            
            for plaid_transaction in plaid_transactions:
                # Check if transaction already exists
                result = await db.execute(
                    select(Transaction).where(
                        Transaction.plaid_transaction_id == plaid_transaction['transaction_id']
                    )
                )
                existing_transaction = result.scalar_one_or_none()
                
                if existing_transaction:
                    # Update existing transaction
                    existing_transaction.amount = Decimal(str(plaid_transaction['amount']))
                    existing_transaction.name = plaid_transaction['name']
                    existing_transaction.merchant_name = plaid_transaction.get('merchant_name')
                    existing_transaction.category = plaid_transaction.get('category')
                    existing_transaction.category_id = plaid_transaction.get('category_id')
                    existing_transaction.pending = plaid_transaction.get('pending', False)
                    existing_transaction.location = None  # Skip location for now
                    existing_transaction.plaid_metadata = None  # Skip metadata for now
                    
                    synced_transactions.append(existing_transaction)
                    
                else:
                    # Get account for this transaction
                    account_result = await db.execute(
                        select(Account).where(
                            Account.plaid_account_id == plaid_transaction['account_id']
                        )
                    )
                    account = account_result.scalar_one_or_none()
                    
                    if account:
                        # Create new transaction
                        new_transaction = Transaction(
                            user_id=user.id,
                            account_id=account.id,
                            plaid_transaction_id=plaid_transaction['transaction_id'],
                            plaid_account_id=plaid_transaction['account_id'],
                            amount=Decimal(str(plaid_transaction['amount'])),
                            iso_currency_code=plaid_transaction.get('iso_currency_code', 'USD'),
                            name=plaid_transaction['name'],
                            merchant_name=plaid_transaction.get('merchant_name'),
                            date=plaid_transaction['date'] if isinstance(plaid_transaction.get('date'), date) else datetime.strptime(plaid_transaction['date'], '%Y-%m-%d').date() if plaid_transaction.get('date') else date.today(),
                            authorized_date=plaid_transaction['authorized_date'] if isinstance(plaid_transaction.get('authorized_date'), date) else datetime.strptime(plaid_transaction['authorized_date'], '%Y-%m-%d').date() if plaid_transaction.get('authorized_date') else None,
                            category=plaid_transaction.get('category'),
                            category_id=plaid_transaction.get('category_id'),
                            transaction_type="debit" if plaid_transaction['amount'] > 0 else "credit",
                            pending=plaid_transaction.get('pending', False),
                            location=None,  # Skip location for now to avoid serialization issues
                            plaid_metadata=None  # Skip metadata for now to avoid serialization issues
                        )
                        
                        db.add(new_transaction)
                        synced_transactions.append(new_transaction)
            
            await db.commit()
            return synced_transactions
            
        except Exception as e:
            logger.error(f"Error syncing transactions: {e}")
            await db.rollback()
            raise Exception(f"Failed to sync transactions: {str(e)}")


# Global Plaid service instance
plaid_service = PlaidService() 