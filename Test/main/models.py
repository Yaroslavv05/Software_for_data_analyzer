from django.db import models
from django.contrib.auth.models import User


class UserProfiles(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    api_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)