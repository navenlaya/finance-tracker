# app/services/plaid.py

from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.date import Date
from app.core.config import settings
from plaid import Configuration, ApiClient

import datetime

# Initialize Plaid client from credentials
def get_plaid_client():
    config = Configuration(
        host={"sandbox": "https://sandbox.plaid.com"}[settings.PLAID_ENV],
        api_key={
            "clientId": settings.PLAID_CLIENT_ID,
            "secret": settings.PLAID_SECRET,
        },
    )
    return plaid_api.PlaidApi(ApiClient(config))

# STEP 1: Create a Link Token for the frontend to initialize Plaid Link
def create_link_token(user_id: str):
    client = get_plaid_client()

    request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(client_user_id=user_id),
        client_name="Finance Tracker",
        products=[Products("transactions")],
        country_codes=[CountryCode("US")],
        language="en",
    )
    response = client.link_token_create(request)
    return response.to_dict()

# STEP 2: Exchange the public token for a permanent access token
def exchange_public_token(public_token: str):
    client = get_plaid_client()
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    return response.to_dict()  # Contains access_token, item_id

# STEP 3: Fetch transactions from the user's linked account
def get_transactions(access_token: str):
    client = get_plaid_client()
    start_date = Date.from_datetime(datetime.datetime.today() - datetime.timedelta(days=30))
    end_date = Date.from_datetime(datetime.datetime.today())

    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )
    response = client.transactions_get(request)
    return response.to_dict()
