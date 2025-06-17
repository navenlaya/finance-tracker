from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_transactions, name='upload-transactions'),
    path('', views.transaction_list, name='transactions-list'),
]
