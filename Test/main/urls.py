from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

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
    path('profile', profile, name='profile'),
    path('change-password', change_password, name='change_password'),
    path('password-change/done/', password_change_done, name='password_change_done'),
    path('change-nickname', change_nickname, name='change_nickname'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main'), name='logout'),
    path('profile/delete/<int:profile_id>/', delete_profile, name='delete_profile'),
    path('edit_profile/<int:profile_id>/', edit_profile, name='edit_profile'),
    path('trade', trade, name='trade'),
    path('waiting', waiting, name='waiting'),
    path('cancel_task', cancel_task, name='cancel_task')
]
