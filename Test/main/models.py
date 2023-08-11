from django.db import models


class MyData(models.Model):
    symbol = models.CharField(max_length=255)
    interval = models.FloatField()
    bound = models.CharField(max_length=255)
    bound_unit = models.CharField(max_length=5)
    start_data = models.CharField(max_length=255)
    end_data = models.CharField(max_length=255)
