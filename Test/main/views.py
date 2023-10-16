from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from .tasks import *
from .models import UserProfiles, TradingData
from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from binance.client import Client
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.conf import settings
import requests
from datetime import time
import os
from django.views.generic.edit import FormView
from django.urls import reverse
from django.views import View


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


class MyFormView(FormView):
    template_name = 'index.html'
    form_class = MyForm

    def form_valid(self, form):
        symbol = form.cleaned_data['symbol']
        interval = form.cleaned_data['interval']
        bound = form.cleaned_data['bound']
        bound_unit = form.cleaned_data['bound_unit']
        start_data = form.cleaned_data['start_data']
        end_data = form.cleaned_data['end_data']

        if symbol not in get_binance_symbols():
            messages.error(self.request, 'Invalid symbol!')
        elif float(bound) < 0:
            messages.error(self.request, 'Bound cannot be negative!')
        elif end_data < start_data:
            messages.error(self.request, 'The end date must be after the start date!')
        else:
            data = {
                'symbol': symbol,
                'interval': interval,
                'bound': bound,
                'bound_unit': bound_unit,
                'start_data': start_data.strftime('%Y-%m-%d'),
                'end_data': end_data.strftime('%Y-%m-%d')
            }

            task = process_data_async.delay(data)
            self.request.session['task_id'] = task.id

            return redirect('process')

    def get_success_url(self):
        return reverse('process')


def process(request):
    return render(request, 'process.html')


class SharesView(FormView):
    template_name = 'shares.html'
    form_class = SharesForm

    def form_valid(self, form):
        symbol = form.cleaned_data['symbol']
        interval = form.cleaned_data['interval']
        bound = form.cleaned_data['bound']
        bound_unit = form.cleaned_data['bound_unit']
        start_data = form.cleaned_data['start_data']
        end_data = form.cleaned_data['end_data']
        symbol_validity = check_symbol_validity(symbol, start_data, end_data)

        if symbol_validity == "invalid symbol":
            messages.error(self.request, 'Invalid symbol!')
        elif float(bound) < 0:
            messages.error(self.request, 'Bound cannot be negative!')
        elif end_data < start_data:
            messages.error(self.request, 'The end date must be after the start date!')
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
            self.request.session['task_id'] = task.id
            print(self.request.session.get('task_id'))
            return redirect('process_shares')

    def get_success_url(self):
        return reverse('process_shares')


def ajax(request):
    date_log = DateLog.objects.get(task_id=request.session.get('task_id'))
    dates_list = [date_log.date]
    return JsonResponse({'dates_list': dates_list})


def process_shares(request):
    return render(request, 'process_shares.html')


def cancel_task(request):
    if request.method == 'POST':
        task_id = request.session.get('task_id')
        try:
            result = AsyncResult(task_id)
            if result.state == 'PENDING':
                result.revoke(terminate=True)
                return redirect('main')
            else:
                return JsonResponse({'message': 'Задача уже выполнена или в процессе выполнения'})
        except Exception as e:
            return JsonResponse({'message': f'Ошибка при отмене задачи: {str(e)}'})

    return JsonResponse({'message': 'Метод запроса должен быть POST'})


class SharesPolygonView(FormView):
    template_name = 'shares_polygon.html'
    form_class = SharesPolygonForm

    def form_valid(self, form):
        symbol = form.cleaned_data['symbol']
        interval = form.cleaned_data['interval']
        bound = form.cleaned_data['bound']
        bound_unit = form.cleaned_data['bound_unit']
        start_data = form.cleaned_data['start_data']
        end_data = form.cleaned_data['end_data']
        api = form.cleaned_data['api']
        pre = form.cleaned_data['choice']
        symbol_validity = check_symbol_validity(symbol, start_data, end_data)

        if symbol_validity == "invalid symbol":
            messages.error(self.request, 'Invalid symbol!')
        elif float(bound) < 0:
            messages.error(self.request, 'Bound cannot be negative!')
        elif end_data < start_data:
            messages.error(self.request, 'The end date must be after the start date!')
        else:
            data = {
                'symbol': symbol,
                'interval': interval,
                'bound': bound,
                'bound_unit': bound_unit,
                'start_data': start_data.strftime('%Y-%m-%d'),
                'end_data': end_data.strftime('%Y-%m-%d'),
                'api': api,
                'pre': pre,
                'task_id': self.request.session.get('task_id')
            }
            task = shares_polygon_async_task.delay(data)
            self.request.session['task_id'] = task.id
            print(self.request.session.get('task_id'))
            return redirect('process_shares')

    def get_success_url(self):
        return reverse('process_shares')


class SharesYFinanceView(FormView):
    template_name = 'shares_yfinance.html'
    form_class = SharesYFinanceForm

    def form_valid(self, form):
        symbol = form.cleaned_data['symbol']
        interval = form.cleaned_data['interval']
        bound = form.cleaned_data['bound']
        bound_unit = form.cleaned_data['bound_unit']
        start_data = form.cleaned_data['start_data']
        end_data = form.cleaned_data['end_data']
        symbol_validity = check_symbol_validity(symbol, start_data, end_data)

        if symbol_validity == "invalid symbol":
            messages.error(self.request, 'Invalid symbol!')
        elif float(bound) < 0:
            messages.error(self.request, 'Bound cannot be negative!')
        elif end_data < start_data:
            messages.error(self.request, 'The end date must be after the start date!')
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
            task = shares_yfinance_async_task.delay(data)
            self.request.session['task_id'] = task.id
            print(self.request.session.get('task_id'))
            return redirect('process_shares')

    def get_success_url(self):
        return reverse('process_shares')


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


class UserLoginView(FormView):
    template_name = 'login.html'
    form_class = UserLoginForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return redirect('profile')

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка авторизации')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('profile')


class ProfileView(View):
    template_name = 'profile.html'

    def get(self, request):
        user_profiles = UserProfiles.objects.filter(user=request.user)
        form = AccountBinanceForm()
        return render(request, self.template_name, {'form': form, 'user_profiles': user_profiles})

    def post(self, request):
        form = AccountBinanceForm(request.POST)

        if form.is_valid():
            user_profile = UserProfiles(user=request.user)
            user_profile.name = form.cleaned_data['name']
            user_profile.api_key = form.cleaned_data['api_key']
            user_profile.secret_key = form.cleaned_data['secret_key']
            user_profile.save()

            return redirect('profile')

        user_profiles = UserProfiles.objects.filter(user=request.user)
        return render(request, self.template_name, {'form': form, 'user_profiles': user_profiles})


def delete_profile(request, profile_id):
    profile = UserProfiles.objects.get(pk=profile_id)
    if profile.user == request.user:
        profile.delete()
    return redirect('profile')


class EditProfileView(View):
    template_name = 'edit_profile.html'

    def get(self, request, profile_id):
        profile = get_object_or_404(UserProfiles, id=profile_id)
        form = AccountBinanceForm(initial={
            'name': profile.name,
            'api_key': profile.api_key,
            'secret_key': profile.secret_key,
        })
        return render(request, self.template_name, {'form': form})

    def post(self, request, profile_id):
        profile = get_object_or_404(UserProfiles, id=profile_id)
        form = AccountBinanceForm(request.POST)

        if form.is_valid():
            profile.name = form.cleaned_data['name']
            profile.api_key = form.cleaned_data['api_key']
            profile.secret_key = form.cleaned_data['secret_key']
            profile.save()
            return redirect('profile')

        return render(request, self.template_name, {'form': form})


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


def trade(request):
    user_id = request.user.id
    if request.method == 'POST':
        form = TradingForm(user_id, request.POST, request.FILES)
        if form.is_valid():
            trading_data = TradingData(user=request.user,
                                       uploaded_file=request.FILES['uploaded_file'],)
            trading_data.save()
            file_path = TradingData.objects.all().last().uploaded_file.name
            user_profile = UserProfiles.objects.get(name=form.cleaned_data['account'])
            api_key = user_profile.api_key
            secret_key = user_profile.secret_key
            async_parse_file_task.delay(file_path=file_path, user_id=request.user.id, symbol=form.cleaned_data['crypto_name'], amount_usdt=form.cleaned_data['usdt_amount'], leverage=form.cleaned_data['leverage'], api_key=api_key, secret_key=secret_key)
    else:
        form = TradingForm(user_id=user_id)
    return render(request, 'trading.html', {'form': form})


def waiting(request):
    return render(request, 'waiting.html')


class TradingView(View):
    template_name = 'tradingview.html'

    def get(self, request):
        form = TradingviewForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TradingviewForm(request.POST, request.FILES)

        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            interval = form.cleaned_data['interval']
            bound = form.cleaned_data['bound']
            bound_unit = form.cleaned_data['bound_unit']
            start_data = form.cleaned_data['start_data']
            end_data = form.cleaned_data['end_data']

            start_time = time(9, 30, 0)
            end_time = time(15, 30, 0)

            start_data = start_data.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second)
            end_data = end_data.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second)

            file_for_big_bar = request.FILES['file_for_big_bar']
            file_for_small_bar = request.FILES['file_for_small_bar']

            file_path_for_big_bar = os.path.join(settings.MEDIA_ROOT, file_for_big_bar.name)
            file_path_for_small_bar = os.path.join(settings.MEDIA_ROOT, file_for_small_bar.name)

            with open(file_path_for_big_bar, 'wb') as f:
                for chunk in file_for_big_bar.chunks():
                    f.write(chunk)

            with open(file_path_for_small_bar, 'wb') as f:
                for chunk in file_for_small_bar.chunks():
                    f.write(chunk)

            data = {
                'symbol': symbol,
                'interval': interval,
                'bound': bound,
                'bound_unit': bound_unit,
                'start_date': str(start_data),
                'end_date': str(end_data),
                'file_for_big_bar': file_path_for_big_bar,
                'file_for_small_bar': file_path_for_small_bar
            }

            task = tradingview_async_task.delay(data)
            request.session['task_id'] = task.id
            return redirect('process_shares')

        return render(request, self.template_name, {'form': form})