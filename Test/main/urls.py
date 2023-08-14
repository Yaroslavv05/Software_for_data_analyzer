from django.urls import path
from .views import main, index, process, result, check_task_status

urlpatterns = [
    path('', main, name='main'),
    path('crypto', index, name='crypto'),
    path('process', process, name='process'),
    path('result', result, name='result'),
    path('check-task-status', check_task_status, name='check_task_status'),
]