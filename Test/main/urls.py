from django.urls import path
from .views import *

urlpatterns = [
    path('', main, name='main'),
    path('crypto', index, name='crypto'),
    path('shares', shares, name='shares'),
    path('process', process, name='process'),
    path('process_shares', process_shares, name='process_shares'),
    path('result', result, name='result'),
    path('check-task-status', check_task_status, name='check_task_status'),
]