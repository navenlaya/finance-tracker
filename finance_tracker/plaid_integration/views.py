from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from transactions.models import Transaction

from plaid2.client import PlaidClient
from dotenv import load_dotenv
import os, json
from datetime import date, timedelta

# Correct imports for models
from plaid2.model.link_token_create_request import LinkTokenCreateRequest
from plaid2.model.link_token_create_request_user import LinkTokenCreateRequestUser

load_dotenv()

# Initialize the Plaid client using .env vars
def get_client():
    return PlaidClient.from_env()


# Serve the frontend page where the user can click "Link Bank"
@login_required
def plaid_link_page(request):
    return render(request, "plaid_integration/link.html")


# Create a link token (needed for frontend Plaid Link)
@login_required
@login_required
def create_link_token(request):
    client = get_client()

    # Create the required user object
    user = LinkTokenCreateRequestUser(client_user_id=str(request.user.id))

    response = client.link_token_create(
        user=user,
        client_name="Finance Tracker",
        products=["transactions"],
        country_codes=["US"],
        language="en"
    )

    # Return JSON response
    return JsonResponse(response.dict())


# Exchange the public_token received from the frontend for an access_token
# Then pull recent transactions and store in DB
@csrf_exempt
@require_POST
@login_required
def exchange_token(request):
    client = get_client()
    data = json.loads(request.body)
    public_token = data.get("public_token")

    # Exchange public token for access token
    exchange = client.item_public_token_exchange(public_token)
    access_token = exchange["access_token"]

    # Save access token to session (you can later store in DB)
    request.session["plaid_access_token"] = access_token

    # Fetch last 30 days of transactions
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    transactions = client.transactions_get(
        access_token=access_token,
        start_date=thirty_days_ago.isoformat(),
        end_date=today.isoformat()
    )["transactions"]

    # Save transactions to database
    for tx in transactions:
        Transaction.objects.create(
            user=request.user,
            date=tx["date"],
            description=tx["name"],
            amount=tx["amount"],
            category=tx["category"][0] if tx.get("category") else "Uncategorized"
        )

    return JsonResponse({"status": "ok", "imported": len(transactions)})
