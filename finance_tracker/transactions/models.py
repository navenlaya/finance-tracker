from django.db import models

# Create your models here.

# Model for a user's uploaded bank transactions
class Transaction(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.date} - {self.description} - {self.amount} ({self.category})"
    
    