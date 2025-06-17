from django import path
from . import views

urlpatters = [
    path('upload/', views.upload_transactions, name='upload-transactions'),
    path('', views.transaction_list, name='transactions-list'),

]