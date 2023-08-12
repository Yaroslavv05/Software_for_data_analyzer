from django.urls import path
from .views import *

urlpatterns = [
    path('', main, name='main'),
    path('crypto', index, name='crypto'),
    path('process', process, name='process'),
    path('result', result, name='result'),
    # path('submit-form', FormSubmissionView.as_view(), name='form-submission'),
]