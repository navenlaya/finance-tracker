from django.http import JsonResponse
from plaid2 import Client
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from transactions.models import Transaction
import json
from datetime import date, timedelta

def get_client():
    return Client.from_environment()

@login_required
def create_link_token(request):
    client = get_client()
    token_response = client.link_token_create({
        "user": {"client_user_id": str(request.user.id)},
        "client_name": "Finance Tracker",
        "products": ["transactions"],
        "country_codes": ["US"],
        "language": "en"
    })
    return JsonResponse(token_response)

@csrf_exempt
@require_POST
@login_required
def exchange_token(request):
    data = json.loads(request.body)
    public_token = data.get("public_token")

    client = get_client()
    exchange = client.item_public_token_exchange(public_token)
    access_token = exchange['access_token']

    # Save the access_token (you can store in DB securely per user)
    request.session['plaid_access_token'] = access_token

    # Fetch transactions
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    response = client.transactions_get(
        access_token,
        start_date=thirty_days_ago.isoformat(),
        end_date=today.isoformat()
    )

    transactions = response['transactions']

    for tx in transactions:
        Transaction.objects.create(
            user=request.user,
            date=tx['date'],
            description=tx['name'],
            amount=tx['amount'],
            category=tx['category'][0] if tx['category'] else 'Uncategorized'
        )

    return JsonResponse({'status': 'ok', 'imported': len(transactions)})
