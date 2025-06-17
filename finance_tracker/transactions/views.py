from django.shortcuts import render, redirect
import csv
from io import TextIOWrapper
from django.contrib.auth.decorators import login_required
from .forms import UploadCSVForm
from .models import Transaction

@login_required
def upload_transactions(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            reader = csv.DictReader(file)

            for row in reader:
                Transaction.objects.create(
                    user=request.user,
                    date=row['Date'],
                    description=row['Description'],
                    category=row.get('Category', 'Uncategorized'),
                    amount=row['Amount']
                )
            return redirect('transactions-list')
    else:
        form = UploadCSVForm()

    return render(request, 'transactions/upload.html', {'form': form})

# Create your views here.
