from django.db import models
from django.contrib.auth.models import User


class UserProfiles(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    api_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)


class TradingData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to='upldfile/')


class DataEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.CharField(max_length=30)
    position = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    amount_usdt = models.CharField(max_length=20)
    leverage = models.CharField(max_length=20)
    api_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)