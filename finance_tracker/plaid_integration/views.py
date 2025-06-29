from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from transactions.models import Transaction

from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid import Configuration, ApiClient

from dotenv import load_dotenv
from datetime import date, timedelta
import os, json

load_dotenv()

def get_client():
    configuration = Configuration(
        host="https://sandbox.plaid.com",  
        api_key={
            'clientId': os.getenv("PLAID_CLIENT_ID"),
            'secret': os.getenv("PLAID_SECRET"),
        }   
    )
    api_client = ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


@login_required
def plaid_link_page(request):
    return render(request, "plaid_integration/link.html")

@login_required
def create_link_token(request):
    client = get_client()

    user = LinkTokenCreateRequestUser(client_user_id=str(request.user.id))

    request_data = LinkTokenCreateRequest(
        user=user,
        client_name="Finance Tracker",
        products=[Products("transactions")],
        country_codes=[CountryCode("US")],
        language="en"
    )

    response = client.link_token_create(request_data)
    return JsonResponse(response.to_dict())

@csrf_exempt
@require_POST
@login_required
def exchange_token(request):
    client = get_client()
    data = json.loads(request.body)
    public_token = data.get("public_token")

    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
    exchange_response = client.item_public_token_exchange(exchange_request)
    access_token = exchange_response['access_token']

    request.session["plaid_access_token"] = access_token

    today = date.today()
    start_date = today - timedelta(days=180)

    transactions_request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=today,
        options=TransactionsGetRequestOptions(count=100, offset=0)
    )

    transactions_response = client.transactions_get(transactions_request)

    for tx in transactions_response['transactions']:
        Transaction.objects.create(
            user=request.user,
            date=tx['date'],
            description=tx['name'],
            amount=tx['amount'],
            category=tx['category'][0] if tx.get("category") else "Uncategorized"
        )

    return JsonResponse({"status": "ok", "imported": len(transactions_response['transactions'])})
