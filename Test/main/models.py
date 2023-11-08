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


class DateLog(models.Model):
    date = models.DateField()
    task_id = models.CharField(max_length=30)


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_running = models.BooleanField(default=False)


class Template(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name_exchange = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    choice = models.CharField(max_length=20)
    api = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    interval = models.CharField(max_length=20)
    bound = models.CharField(max_length=100)
    bound_unit = models.CharField(max_length=10)
    start_date = models.CharField(max_length=100)
    end_date = models.CharField(max_length=100)
    min_interval = models.CharField(max_length=100)