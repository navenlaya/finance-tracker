from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_transactions, name='upload-transactions'),
    path('', views.transaction_list, name='transactions-list'),
    path('forecast/', views.forecast_view, name='forcast'), 
    path('insights/', views.insights_view, name='insights'),
]
