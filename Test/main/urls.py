from django.urls import path
from .views import *

urlpatterns = [
    path('', main, name='main'),
    path('crypto', index, name='crypto'),
    path('result', result, name='result')
]