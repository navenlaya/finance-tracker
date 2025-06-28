from django.urls import path
from . import views

urlpatterns = [
    path("create-link-token/", views.create_link_token, name="create-link-token"),
    path("exchange-token/", views.exchange_token, name="exchange-token"),
    path("connect/", views.plaid_link_page, name="plaid-link-page"),  # ⬅️ New
]
