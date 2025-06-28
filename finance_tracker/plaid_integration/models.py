from django.db import models
from django.contrib.auth.models import User

# Stores each user's Plaid item information
class PlaidItem(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=200)
    item_id = models.CharField(max_length=200)
