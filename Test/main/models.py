from django.db import models
from django.contrib.auth.models import User


class UserProfiles(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    api_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)


class TradingData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.CharField(max_length=20)
    uploaded_file = models.FileField(upload_to='upldfile/')
    crypto_name = models.CharField(max_length=100)
    usdt_amount = models.CharField(max_length=50)
    leverage = models.CharField(max_length=50)