from django.urls import path
from .views import *

urlpatterns = [
    path('', main, name='main'),
    path('crypto-binance', index, name='crypto'),
    path('shares-twelvedata', shares, name='shares'),
    path('process', process, name='process'),
    path('process_shares', process_shares, name='process_shares'),
    path('result', result, name='result'),
    path('check-task-status', check_task_status, name='check_task_status'),
    path('shares-polygon', shares_polygon, name='shares_polygon'),
    path('login', user_login, name='login'),
    path('profile', profile, name='profile')
]