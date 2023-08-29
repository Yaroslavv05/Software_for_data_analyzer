from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MyForm, SharesForm, SharesPolygonForm, UserLoginForm, PasswordChangeForm, FirstNameChangeForm, AccountBinanceForm
from .tasks import process_data_async, shared_async_task, shares_polygon_async_task
from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from binance.client import Client
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth import login, logout
import requests
import os


def get_binance_symbols():
    client = Client()
    exchange_info = client.get_exchange_info()
    symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]
    return symbols


def check_symbol_validity(symbol, start_data, end_data):
    api_key = "7e1f42d9a4f743749ffa9e77958e06a4"
    url = f"https://api.twelvedata.com/time_series?apikey={api_key}&interval=1min&symbol={symbol}&timezone=utc&start_date={start_data}&end_date={end_data}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "status" in data and data["status"] == "error" and "message" in data and "**symbol** not found" in data[
            "message"]:
            return "invalid symbol"
        else:
            return "valid symbol"
    else:
        return "error"


def main(request):
    return render(request, 'main.html')


def index(request):
    form = MyForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            interval = form.cleaned_data['interval']
            bound = form.cleaned_data['bound']
            bound_unit = form.cleaned_data['bound_unit']
            start_data = form.cleaned_data['start_data']
            end_data = form.cleaned_data['end_data']
            if symbol not in get_binance_symbols():
                messages.error(request, 'Invalid symbol!')
            elif float(bound) < 0:
                messages.error(request, 'Bound cannot be negative!')
            elif end_data < start_data:
                messages.error(request, 'The end date must be after the start date!')
            else:
                data = {
                    'symbol': symbol,
                    'interval': interval,
                    'bound': bound,
                    'bound_unit': bound_unit,
                    'start_data': start_data.strftime('%Y-%m-%d'),
                    'end_data': end_data.strftime('%Y-%m-%d')
                }
                print(data)
                task = process_data_async.delay(data)
                request.session['task_id'] = task.id
                print(request.session.get('task_id'))
                return redirect('process')
    else:
        form = MyForm()
    return render(request, 'index.html', {'form': form})


def process(request):
    return render(request, 'process.html')


def shares(request):
    form = SharesForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            interval = form.cleaned_data['interval']
            bound = form.cleaned_data['bound']
            bound_unit = form.cleaned_data['bound_unit']
            start_data = form.cleaned_data['start_data']
            end_data = form.cleaned_data['end_data']
            symbol_validity = check_symbol_validity(symbol, start_data, end_data)
            if symbol_validity == "invalid symbol":
                messages.error(request, 'Invalid symbol!')
            elif float(bound) < 0:
                messages.error(request, 'Bound cannot be negative!')
            elif end_data < start_data:
                messages.error(request, 'The end date must be after the start date!')
            else:
                data = {
                    'symbol': symbol,
                    'interval': interval,
                    'bound': bound,
                    'bound_unit': bound_unit,
                    'start_data': start_data.strftime('%Y-%m-%d'),
                    'end_data': end_data.strftime('%Y-%m-%d')
                }
                task = shared_async_task.delay(data)
                request.session['task_id'] = task.id
                print(request.session.get('task_id'))
                return redirect('process_shares')
    else:
        form = SharesForm()
    return render(request, 'shares.html', {'form': form})


def process_shares(request):
    return render(request, 'process_shares.html')


def shares_polygon(request):
    form = SharesPolygonForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            interval = form.cleaned_data['interval']
            bound = form.cleaned_data['bound']
            bound_unit = form.cleaned_data['bound_unit']
            start_data = form.cleaned_data['start_data']
            end_data = form.cleaned_data['end_data']
            symbol_validity = check_symbol_validity(symbol, start_data, end_data)
            if symbol_validity == "invalid symbol":
                messages.error(request, 'Invalid symbol!')
            elif float(bound) < 0:
                messages.error(request, 'Bound cannot be negative!')
            elif end_data < start_data:
                messages.error(request, 'The end date must be after the start date!')
            else:
                data = {
                    'symbol': symbol,
                    'interval': interval,
                    'bound': bound,
                    'bound_unit': bound_unit,
                    'start_data': start_data.strftime('%Y-%m-%d'),
                    'end_data': end_data.strftime('%Y-%m-%d')
                }
                task = shares_polygon_async_task.delay(data)
                request.session['task_id'] = task.id
                print(request.session.get('task_id'))
                return redirect('process_shares')

    else:
        form = SharesPolygonForm()
    return render(request, 'shares_polygon.html', {'form': form})


def check_task_status(request):
    task_id = request.session.get('task_id')
    print(task_id)
    if task_id:
        task = AsyncResult(task_id)
        if task.ready():
            if task.successful():
                file_path = task.result
                request.session['file_path'] = file_path
                return JsonResponse({'status': 'completed', 'file_path': file_path})
            else:
                print('failed')
                return JsonResponse({'status': 'Task failed.'})
        else:
            print('running')
            return JsonResponse({'status': 'running'})
    else:
        print('not found')
        return JsonResponse({'status': 'task_id_not_found'})


def result(request):
    file_path = request.session.get('file_path')
    if file_path and os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    else:
        return HttpResponse("File not found.")


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Ошибка авторизации')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


def profile(request):
    form = AccountBinanceForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            pass
    else:
        form = AccountBinanceForm()
    return render(request, 'profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password1 = form.cleaned_data['new_password1']
            new_password2 = form.cleaned_data['new_password2']

            if not request.user.check_password(old_password):
                messages.error(request, 'Старый пароль неверен.')
            elif new_password1 != new_password2:
                messages.error(request, 'Новые пароли не совпадают.')
            else:
                request.user.set_password(new_password1)
                request.user.save()
                messages.success(request, 'Пароль успешно изменен.')
                return redirect('password_change_done')
    else:
        form = PasswordChangeForm()
    return render(request, 'change_password.html', {'form': form})


def change_nickname(request):
    if request.method == 'POST':
        form = FirstNameChangeForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['new_nickname']
            request.user.save()
            messages.success(request, f'Ваше имя было измененно на {form.cleaned_data["new_nickname"]}')
            return redirect('change_nickname')
    else:
        form = FirstNameChangeForm()
    return render(request, 'change_nickname.html', {'form': form})


def password_change_done(request):
    logout(request)
    return redirect('login')

