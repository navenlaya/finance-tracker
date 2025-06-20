from django.shortcuts import render, redirect
import csv
from io import TextIOWrapper
from django.contrib.auth.decorators import login_required
from .forms import UploadCSVForm
from .models import Transaction
from .utils import categorize

# For Forcast View
import pandas as pd
from prophet import Prophet


@login_required
# Transaction Upload View
def upload_transactions(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            reader = csv.DictReader(file)

            # Clear existing transactions for the user before uploading new ones
            for row in reader:
                Transaction.objects.create(
                    user=request.user,
                    date=row['Date'],
                    description=row['Description'],
                    category=row.get('Category') or categorize(row['Description']), 
                    amount=row['Amount']
                )
            return redirect('transactions-list')
    else:
        form = UploadCSVForm()

    return render(request, 'transactions/upload.html', {'form': form})

@login_required
# Transaction List View
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'transactions/list.html', {'transactions': transactions})

@login_required
def forecast_view(request):
    # Get user's transactions
    transactions = Transaction.objects.filter(user=request.user).order_by('date')

    df = pd.DataFrame.from_records(
        transactions.values('date', 'amount'),

    )

    df = df.groupby('date').sum().reset_index()

    if df.empty:
        return (request, 'transactions/forecast.html', {'message': 'No data to forecast'})

    df['ds'] = pd.to_datetime(df['date'])
    df['y'] = df['amount']

    # Create and train prophet model
    model = Prophet()
    model.fit(df[['ds', 'y']])

    # Create future days
    future = model.make_future_dataFrame(period=30)
    forecast = model.predict(future)

    # Convert to JSON for fontend
    forcast_json = forecast [['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_json(orient='records', date_format='iso')

    return render(request, 'transactions/forcast.html', {
        'forcast_json': forcast_json,
        'forcast_table': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(10).to_html(classes='table table-striped'),
    })