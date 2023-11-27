from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from .tasks import *
from .models import *
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
            
    def form_valid(self, form):
        symbol = form.cleaned_data['symbol']
        interval = form.cleaned_data['interval']
        bound_up = form.cleaned_data['bound_up']
        bound_unit_up = form.cleaned_data['bound_unit_up']
        bound_low = form.cleaned_data['bound_low']
        bound_unit_low = form.cleaned_data['bound_unit_low']
        start_data = form.cleaned_data['start_data']
        end_data = form.cleaned_data['end_data']
        
        if form.cleaned_data['use_template'] == True:
            flipped_interval_mapping = {
                '1 minute': 0.0166666667,
                '3 minute': 0.05,
                '5 minute': 0.0833333333,
                '15 minute': 0.25,
                '30 minute': 0.5,
                '1 hour': 1,
                '2 hour': 2,
                '4 hour': 4,
                '6 hour': 6,
                '8 hour': 8,
                '12 hour': 12,
                '1 day': 24,
                '3 day': 72,
                '1 week': 168,
                '1 month': 720
            }
            template = get_object_or_404(Template, id=form.cleaned_data['selected_template'])
            print(flipped_interval_mapping[template.interval],)
            form = MyForm(user=self.request.user.id, initial={
                'symbol': template.symbol,
                'interval': flipped_interval_mapping[template.interval],
                'bound_up': template.bound_up,
                'bound_unit_up': template.bound_unit_up,
                'bound_low': template.bound_low,
                'bound_unit_low': template.bound_unit_low,
                'start_data': datetime.strptime(template.start_date, '%Y-%m-%d %H:%M:%S'),
                'end_data': datetime.strptime(template.end_date, '%Y-%m-%d %H:%M:%S')
            })
            return render(self.request, self.template_name, {'form': form})
        else:
            if form.cleaned_data['symbol'] and form.cleaned_data['interval'] and form.cleaned_data['bound_up'] and form.cleaned_data['bound_unit_up'] and form.cleaned_data['bound_low'] and form.cleaned_data['bound_unit_low'] and form.cleaned_data['start_data'] and form.cleaned_data['end_data']:
                if symbol not in get_binance_symbols():
                    messages.error(self.request, 'Invalid symbol!')
                    form = MyForm(user=self.request.user.id,initial={
                        'symbol': '',
                        'interval': form.cleaned_data['interval'],
                        'bound_up': form.cleaned_data['bound_up'],
                        'bound_unit_up': form.cleaned_data['bound_unit_up'],
                        'bound_low': form.cleaned_data['bound_low'],
                        'bound_unit_low': form.cleaned_data['bound_unit_low'],
                        'start_data': form.cleaned_data['start_data'],
                        'end_data': form.cleaned_data['end_data'],
                    })
                    return render(self.request, self.template_name, {'form': form})
                elif float(bound_up) < 0:
                    messages.error(self.request, 'Bound cannot be negative!')
                    form = MyForm(user=self.request.user.id,initial={
                        'symbol': form.cleaned_data['symbol'],
                        'interval': form.cleaned_data['interval'],
                        'bound_up': '',
                        'bound_low': form.cleaned_data['bound_low'],
                        'bound_unit_up': form.cleaned_data['bound_unit_up'],
                        'bound_unit_low': form.cleaned_data['bound_unit_low'],
                        'start_data': form.cleaned_data['start_data'],
                        'end_data': form.cleaned_data['end_data'],
                    })
                    return render(self.request, self.template_name, {'form': form})
                elif float(bound_low) < 0:
                    messages.error(self.request, 'Bound cannot be negative!')
                    form = MyForm(user=self.request.user.id,initial={
                        'symbol': form.cleaned_data['symbol'],
                        'interval': form.cleaned_data['interval'],
                        'bound_up': form.cleaned_data['bound_up'],
                        'bound_low': '',
                        'bound_unit_up': form.cleaned_data['bound_unit_up'],
                        'bound_unit_low': form.cleaned_data['bound_unit_low'],
                        'start_data': form.cleaned_data['start_data'],
                        'end_data': form.cleaned_data['end_data'],
                    })
                    return render(self.request, self.template_name, {'form': form})
                elif end_data < start_data:
                    messages.error(self.request, 'The end date must be after the start date!')
                    form = MyForm(user=self.request.user.id,initial={
                        'symbol':  form.cleaned_data['symbol'],
                        'interval': form.cleaned_data['interval'],
                        'bound_up': form.cleaned_data['bound_up'],
                        'bound_unit_up': form.cleaned_data['bound_unit_up'],
                        'bound_low': form.cleaned_data['bound_low'],
                        'bound_unit_low': form.cleaned_data['bound_unit_low'],
                        'start_data': form.cleaned_data['start_data'],
                        'end_data': '',
                    })
                    return render(self.request, self.template_name, {'form': form})
                else:
                    if Task.objects.filter(user=self.request.user, is_running=True).exists():
                        messages.error(self.request, 'Задача уже выполняется. Подождите завершения.')
                        form = MyForm(user=self.request.user.id,initial={
                            'symbol':  form.cleaned_data['symbol'],
                            'interval': form.cleaned_data['interval'],
                            'bound_up': form.cleaned_data['bound_up'],
                            'bound_unit_up': form.cleaned_data['bound_unit_up'],
                            'bound_low': form.cleaned_data['bound_low'],
                            'bound_unit_low': form.cleaned_data['bound_unit_low'],
                            'start_data': form.cleaned_data['start_data'],
                            'end_data': form.cleaned_data['end_data'],
                        })
                        return render(self.request, self.template_name, {'form': form})
                    else:
                        if form.cleaned_data['save_tamplates'] == True:
                            interval_mapping = {
                                0.0166666667: '1 minute',
                                0.05: '3 minute',
                                0.0833333333: '5 minute',
                                0.25: '15 minute',
                                0.5: '30 minute',
                                1.0: '1 hour',
                                2.0: '2 hour',
                                4.0: '4 hour',
                                6.0: '6 hour',
                                8.0: '8 hour',
                                12.0: '12 hour',
                                24.0: '1 day',
                                72.0: '3 day',
                                168.0: '1 week',
                                720.0: '1 month'
                            }
                            Template.objects.create(user=self.request.user, name_exchange='Binance', name=f'Binance/{symbol}/{interval}/{start_data}/{end_data}/{bound_up}/{bound_unit_up}/{bound_low}/{bound_unit_low}', 
                                                    symbol=symbol, interval=interval_mapping[float(interval)], 
                                                    bound_up=bound_up, bound_unit_up=bound_unit_up, bound_low=bound_low, bound_unit_low=bound_unit_low, start_date=start_data, end_date=end_data, min_interval=form.cleaned_data['custom_radio_field'])
                            messages.success(self.request, 'Шаблон был сохранен!')
                        task = Task.objects.create(user=self.request.user, is_running=True)
                        data = {
                            'symbol': symbol,
                            'interval': interval,
                            'bound_up': bound_up,
                            'bound_unit_up': bound_unit_up,
                            'bound_low': bound_low,
                            'bound_unit_low': bound_unit_low,
                            'start_data': start_data.strftime('%Y-%m-%d'),
                            'end_data': end_data.strftime('%Y-%m-%d'),
                            'us': self.request.user.id
                        }

                        task = process_data_async.delay(data)
                        self.request.session['task_id'] = task.id

                        return redirect('process')
            else:
                messages.error(self.request, 'Пожалуйста, заполните все поля.')
                form = MyForm(user=self.request.user.id,initial={
                    'symbol':  form.cleaned_data['symbol'],
                    'interval': form.cleaned_data['interval'],
                    'bound_up': form.cleaned_data['bound_up'],
                    'bound_unit_up': form.cleaned_data['bound_unit_up'],
                    'bound_low': form.cleaned_data['bound_low'],
                    'bound_unit_low': form.cleaned_data['bound_unit_low'],
                    'start_data': form.cleaned_data['start_data'],
                    'end_data': form.cleaned_data['end_data'],
                })
                return render(self.request, self.template_name, {'form': form})
    def get_success_url(self):
        return reverse('process')


def process(request):
    return render(request, 'process.html')


class SharesView(FormView):
    template_name = 'shares.html'
    form_class = SharesForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        symbol = form.cleaned_data['symbol']
        interval = form.cleaned_data['interval']
        bound_up = form.cleaned_data['bound_up']
        bound_unit_up = form.cleaned_data['bound_unit_up']
        bound_low = form.cleaned_data['bound_low']
        bound_unit_low = form.cleaned_data['bound_unit_low']
        start_data = form.cleaned_data['start_data']
        end_data = form.cleaned_data['end_data']
        symbol_validity = check_symbol_validity(symbol, start_data, end_data)
        
        if form.cleaned_data['use_template'] == True:
            template = get_object_or_404(Template, id=form.cleaned_data['selected_template'])
            interval_mapping = {
                '1 minute': '1min',
                '5 minute': '5min',
                '15 minute': '15min',
                '30 minute': '30min',
                '45 minute': '45min',
                '1 hour': '1h',
                '2 hour': '2h',
                '4 hour': '4h',
                '1 day': '1day',
                '1 week': '1week',
                '1 month': '1month'
            }
            form = SharesForm(user=self.request.user.id, initial={
                'symbol': template.symbol,
                'interval': interval_mapping[template.interval],
                'bound': template.bound,
                'bound_unit': template.bound_unit,
                'start_data': datetime.strptime(template.start_date, '%Y-%m-%d %H:%M:%S'),
                'end_data': datetime.strptime(template.end_date, '%Y-%m-%d %H:%M:%S')
            })
            return render(self.request, self.template_name, {'form': form})
        else:
            if form.cleaned_data['symbol'] and form.cleaned_data['interval'] and form.cleaned_data['bound_up'] and form.cleaned_data['bound_unit_up'] and form.cleaned_data['bound_low'] and form.cleaned_data['bound_unit_low'] and form.cleaned_data['start_data'] and form.cleaned_data['end_data']:
                if symbol_validity == "invalid symbol":
                    messages.error(self.request, 'Invalid symbol!')
                    form = SharesForm(user=self.request.user.id, initial={
                        'symbol': '',
                        'interval': form.cleaned_data['interval'],
                        'bound': form.cleaned_data['bound'],
                        'bound_unit': form.cleaned_data['bound_unit'],
                        'start_data': form.cleaned_data['start_data'],
                        'end_data': form.cleaned_data['end_data'],
                    })
                    return render(self.request, self.template_name, {'form': form})
                elif float(bound_up) < 0:
                    messages.error(self.request, 'Bound cannot be negative!')
                    form = SharesForm(user=self.request.user.id, initial={
                        'symbol':  form.cleaned_data['symbol'],
                        'interval': form.cleaned_data['interval'],
                        'bound': '',
                        'bound_unit': form.cleaned_data['bound_unit'],
                        'start_data': form.cleaned_data['start_data'],
                        'end_data': form.cleaned_data['end_data'],
                    })
                    return render(self.request, self.template_name, {'form': form})
                elif float(bound_low) < 0:
                    messages.error(self.request, 'Bound cannot be negative!')
                    form = SharesForm(user=self.request.user.id, initial={
                        'symbol':  form.cleaned_data['symbol'],
                        'interval': form.cleaned_data['interval'],
                        'bound': '',
                        'bound_unit': form.cleaned_data['bound_unit'],
                        'start_data': form.cleaned_data['start_data'],
                        'end_data': form.cleaned_data['end_data'],
                    })
                    return render(self.request, self.template_name, {'form': form})
                elif end_data < start_data:
                    messages.error(self.request, 'The end date must be after the start date!')
                    form = SharesForm(user=self.request.user.id,initial={
                        'symbol':  form.cleaned_data['symbol'],
                        'interval': form.cleaned_data['interval'],
                        'bound': form.cleaned_data['bound'],
                        'bound_unit': form.cleaned_data['bound_unit'],
                        'start_data': form.cleaned_data['start_data'],
                        'end_data': '',
                    })
                    return render(self.request, self.template_name, {'form': form})
                else:
                    if Task.objects.filter(user=self.request.user, is_running=True).exists():
                        messages.error(self.request, 'Задача уже выполняется. Подождите завершения.')
                        form = SharesForm(user=self.request.user.id,initial={
                            'symbol':  form.cleaned_data['symbol'],
                            'interval': form.cleaned_data['interval'],
                            'bound': form.cleaned_data['bound'],
                            'bound_unit': form.cleaned_data['bound_unit'],
                            'start_data': form.cleaned_data['start_data'],
                            'end_data': form.cleaned_data['end_data'],
                        })
                        return render(self.request, self.template_name, {'form': form})
                    else:
                        if form.cleaned_data['save_tamplates'] == True:
                            interval_mapping = {
                                '1min': '1 minute',
                                '5min': '5 minute',
                                '15min': '15 minute',
                                '30min': '30 minute',
                                '45min': '45 minute',
                                '1h': '1 hour',
                                '2h': '2 hour',
                                '4h': '4 hour',
                                '1day': '1 day',
                                '1week': '1 week',
                                '1month': '1 month'
                            }
                            Template.objects.create(user=self.request.user, name_exchange='TwelveData', name=f'TwelveData/{symbol}/{interval}/{start_data}/{end_data}/{bound_up}/{bound_unit_up}/{bound_low}/{bound_unit_low}', 
                                                    symbol=symbol, interval=interval_mapping[interval], bound_up=bound_up, bound_unit_up=bound_unit_up, bound_low=bound_low, bound_unit=bound_unit_low, 
                                                    start_date=start_data, end_date=end_data, min_interval=form.cleaned_data['custom_radio_field'])
                            messages.success(self.request, 'Шаблон был сохранен!')
                        task = Task.objects.create(user=self.request.user, is_running=True)
                        data = {
                            'symbol': symbol,
                            'interval': interval,
                            'bound_up': bound_up,
                            'bound_unit_up': bound_unit_up,
                            'bound_low': bound_low,
                            'bound_unit_low': bound_unit_low,
                            'start_data': start_data.strftime('%Y-%m-%d'),
                            'end_data': end_data.strftime('%Y-%m-%d'),
                            'us': self.request.user.id
                        }
                        task = shared_async_task.delay(data)
                        self.request.session['task_id'] = task.id
                        print(self.request.session.get('task_id'))
                        return redirect('process_shares')
            else:
                messages.error(self.request, 'Пожалуйста, заполните все поля.')
                form = SharesForm(user=self.request.user.id,initial={
                    'symbol':  form.cleaned_data['symbol'],
                    'interval': form.cleaned_data['interval'],
                    'bound': form.cleaned_data['bound'],
                    'bound_unit': form.cleaned_data['bound_unit'],
                    'start_data': form.cleaned_data['start_data'],
                    'end_data': form.cleaned_data['end_data'],
                })
                return render(self.request, self.template_name, {'form': form})
        
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
                task = Task.objects.get(user=request.user, is_running=True)
                task.is_running = False
                task.save()
                return redirect('main')
            else:
                task = Task.objects.get(user=request.user, is_running=True)
                task.is_running = False
                task.save()
                return redirect('main')
        except Exception as e:
            return redirect('main')

    return JsonResponse({'message': 'Метод запроса должен быть POST'})


class SharesPolygonView(FormView):
    template_name = 'shares_polygon.html'
    form_class = SharesPolygonForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        symbol = form.cleaned_data['symbol']
        interval = form.cleaned_data['interval']
        bound_up = form.cleaned_data['bound_up']
        bound_unit_up = form.cleaned_data['bound_unit_up']
        bound_low = form.cleaned_data['bound_low']
        bound_unit_low = form.cleaned_data['bound_unit_low']
        start_data = form.cleaned_data['start_data']
        end_data = form.cleaned_data['end_data']
        pre = form.cleaned_data['choice']
        symbol_validity = check_symbol_validity(symbol, start_data, end_data)
        
        if form.cleaned_data['use_template'] == True:
            template = get_object_or_404(Template, id=form.cleaned_data['selected_template'])
            form = SharesPolygonForm(user=self.request.user.id, initial={
                'choice': template.choice,
                'symbol': template.symbol,
                'interval': template.interval,
                'bound_up': template.bound_up,
                'bound_unit_up': template.bound_unit_up,
                'bound_low': template.bound_low,
                'bound_unit_low': template.bound_unit_low,
                'custom_radio_field': template.min_interval,
                'start_data': datetime.strptime(template.start_date, '%Y-%m-%d %H:%M:%S'),
                'end_data': datetime.strptime(template.end_date, '%Y-%m-%d %H:%M:%S')
            })
            return render(self.request, self.template_name, {'form': form})
        else:
            if (form.cleaned_data['symbol'] and form.cleaned_data['interval'] and form.cleaned_data['bound_up'] and form.cleaned_data['bound_unit_up'] and form.cleaned_data['bound_low'] and form.cleaned_data['bound_unit_low'] and form.cleaned_data['start_data'] and form.cleaned_data['end_data'] and form.cleaned_data['choice'] and form.cleaned_data['custom_radio_field']):
                if symbol_validity == "invalid symbol":
                    messages.error(self.request, 'Неверный символ!')
                    form = SharesPolygonForm(user=self.request.user.id,initial={
                        'choice': form.cleaned_data['choice'],
                        'symbol': '',
                        'interval': form.cleaned_data['interval'],
                        'bound_up': form.cleaned_data['bound_up'],
                        'bound_unit_up': form.cleaned_data['bound_unit_up'],
                        'bound_low': form.cleaned_data['bound_low'],
                        'bound_unit_low': form.cleaned_data['bound_unit_low'],
                        'custom_radio_field': form.cleaned_data['custom_radio_field'],
                        'start_data': form.cleaned_data['start_data'],
                        'end_data': form.cleaned_data['end_data']
                    })
                    return render(self.request, self.template_name, {'form': form})
                elif float(bound_up) < 0:
                    messages.error(self.request, 'Связка не может быть отрицательной!')
                    form = SharesPolygonForm(user=self.request.user.id,initial={
                        'choice': form.cleaned_data['choice'],
                        'symbol': form.cleaned_data['symbol'],
                        'interval': form.cleaned_data['interval'],
                        'bound_up': '',
                        'bound_unit_up': form.cleaned_data['bound_unit_up'],
                        'bound_low': form.cleaned_data['bound_low'],
                        'bound_unit_low': form.cleaned_data['bound_unit_low'],
                        'custom_radio_field': form.cleaned_data['custom_radio_field'],
                        'start_data': form.cleaned_data['start_data'],
                        'end_data': form.cleaned_data['end_data']
                    })
                    return render(self.request, self.template_name, {'form': form})
                elif float(bound_low) < 0:
                    messages.error(self.request, 'Связка не может быть отрицательной!')
                    form = SharesPolygonForm(user=self.request.user.id,initial={
                        'choice': form.cleaned_data['choice'],
                        'symbol': form.cleaned_data['symbol'],
                        'interval': form.cleaned_data['interval'],
                        'bound_up': form.cleaned_data['bound_up'],
                        'bound_unit_up': form.cleaned_data['bound_unit_up'],
                        'bound_low': '',
                        'bound_unit_low': form.cleaned_data['bound_unit_low'],
                        'custom_radio_field': form.cleaned_data['custom_radio_field'],
                        'start_data': form.cleaned_data['start_data'],
                        'end_data': form.cleaned_data['end_data']
                    })
                    return render(self.request, self.template_name, {'form': form})
                elif end_data < start_data:
                    messages.error(self.request, 'Дата окончания должна быть позже даты начала!')
                    form = SharesPolygonForm(user=self.request.user.id,initial={
                        'choice': form.cleaned_data['choice'],
                        'symbol': form.cleaned_data['symbol'],
                        'interval': form.cleaned_data['interval'],
                        'bound_up': form.cleaned_data['bound_up'],
                        'bound_unit_up': form.cleaned_data['bound_unit_up'],
                        'bound_low': form.cleaned_data['bound_low'],
                        'bound_unit_low': form.cleaned_data['bound_unit_low'],
                        'custom_radio_field': form.cleaned_data['custom_radio_field'],
                        'start_data': form.cleaned_data['start_data'],
                        'end_data': ''
                    })
                    return render(self.request, self.template_name, {'form': form})
                else:
                    if Task.objects.filter(user=self.request.user, is_running=True).exists():
                        messages.error(self.request, 'Задача уже выполняется. Подождите завершения.')
                        form = SharesPolygonForm(user=self.request.user.id,initial={
                            'choice': form.cleaned_data['choice'],
                            'symbol': form.cleaned_data['symbol'],
                            'interval': form.cleaned_data['interval'],
                            'bound_up': form.cleaned_data['bound_up'],
                            'bound_unit_up': form.cleaned_data['bound_unit_up'],
                            'bound_low': form.cleaned_data['bound_low'],
                            'bound_unit_low': form.cleaned_data['bound_unit_low'],
                            'custom_radio_field': form.cleaned_data['custom_radio_field'],
                            'start_data': form.cleaned_data['start_data'],
                            'end_data': form.cleaned_data['end_data']
                        })
                        return render(self.request, self.template_name, {'form': form})
                    else:
                        if form.cleaned_data['save_tamplates'] == True:
                            Template.objects.create(user=self.request.user, name_exchange='Polygon', name=f'Polygon/{symbol}/{interval}/{start_data}/{end_data}/{bound_up}/{bound_unit_up}/{form.cleaned_data["custom_radio_field"]}с', choice=pre, 
                                                    symbol=symbol, interval=interval, bound_up=bound_up, bound_unit_up=bound_unit_up, bound_low=bound_low, bound_unit_low=bound_unit_low, start_date=start_data, 
                                                    end_date=end_data, min_interval=form.cleaned_data['custom_radio_field'])
                            messages.success(self.request, 'Шаблон был сохранен!')
                        task = Task.objects.create(user=self.request.user, is_running=True)
                        data = {
                            'symbol': symbol,
                            'interval': interval,
                            'bound_up': bound_up,
                            'bound_unit_up': bound_unit_up,
                            'bound_low': bound_low,
                            'bound_unit_low': bound_unit_low,
                            'start_data': start_data.strftime('%Y-%m-%d'),
                            'end_data': end_data.strftime('%Y-%m-%d'),
                            'api': 'EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz',
                            'pre': pre,
                            'task_id': self.request.session.get('task_id'),
                            'us': self.request.user.id,
                            'min_interval': form.cleaned_data['custom_radio_field']
                        }
                        task = shares_polygon_async_task.delay(data)
                        self.request.session['task_id'] = task.id
                        print(self.request.session.get('task_id'))
                        return redirect('process_shares')
            else:
                messages.error(self.request, 'Пожалуйста, заполните все поля.')
                form = SharesPolygonForm(user=self.request.user.id,initial={
                    'choice': form.cleaned_data['choice'],
                    'symbol': form.cleaned_data['symbol'],
                    'interval': form.cleaned_data['interval'],
                    'bound': form.cleaned_data['bound'],
                    'bound_unit': form.cleaned_data['bound_unit'],
                    'custom_radio_field': form.cleaned_data['custom_radio_field'],
                    'start_data': form.cleaned_data['start_data'],
                    'end_data': form.cleaned_data['end_data']
                })
                return render(self.request, self.template_name, {'form': form})           

    def get_success_url(self):
        return reverse('process_shares')


class SharesYFinanceView(FormView):
    template_name = 'shares_yfinance.html'
    form_class = SharesYFinanceForm

    def form_valid(self, form):
        symbol = form.cleaned_data['symbol']
        interval = form.cleaned_data['interval']
        bound_up = form.cleaned_data['bound_up']
        bound_unit_up = form.cleaned_data['bound_unit_up']
        bound_low = form.cleaned_data['bound_low']
        bound_unit_low = form.cleaned_data['bound_unit_low']
        start_data = form.cleaned_data['start_data']
        end_data = form.cleaned_data['end_data']
        symbol_validity = check_symbol_validity(symbol, start_data, end_data)

        if symbol_validity == "invalid symbol":
            messages.error(self.request, 'Invalid symbol!')
            form = SharesYFinanceForm(initial={
                'symbol':  '',
                'interval': form.cleaned_data['interval'],
                'bound': form.cleaned_data['bound'],
                'bound_unit': form.cleaned_data['bound_unit'],
                'start_data': form.cleaned_data['start_data'],
                'end_data': form.cleaned_data['end_data'],
            })
            return render(self.request, self.template_name, {'form': form})
        elif float(bound_up) < 0:
            messages.error(self.request, 'Bound cannot be negative!')
            form = SharesYFinanceForm(initial={
                'symbol':  form.cleaned_data['symbol'],
                'interval': form.cleaned_data['interval'],
                'bound_up': '',
                'bound_unit_up': form.cleaned_data['bound_unit_up'],
                'bound_low': form.cleaned_data['bound_low'],
                'bound_unit_low': form.cleaned_data['bound_unit_low'],
                'start_data': form.cleaned_data['start_data'],
                'end_data': form.cleaned_data['end_data'],
            })
            return render(self.request, self.template_name, {'form': form})
        elif float(bound_low) < 0:
            messages.error(self.request, 'Bound cannot be negative!')
            form = SharesYFinanceForm(initial={
                'symbol':  form.cleaned_data['symbol'],
                'interval': form.cleaned_data['interval'],
                'bound_up': form.cleaned_data['bound_up'],
                'bound_unit_up': form.cleaned_data['bound_unit_up'],
                'bound_low': '',
                'bound_unit_low': form.cleaned_data['bound_unit_low'],
                'start_data': form.cleaned_data['start_data'],
                'end_data': form.cleaned_data['end_data'],
            })
            return render(self.request, self.template_name, {'form': form})
        elif end_data < start_data:
            messages.error(self.request, 'The end date must be after the start date!')
            form = SharesYFinanceForm(initial={
                'symbol':  form.cleaned_data['symbol'],
                'interval': form.cleaned_data['interval'],
                'bound': form.cleaned_data['bound'],
                'bound_unit': form.cleaned_data['bound_unit'],
                'start_data': form.cleaned_data['start_data'],
                'end_data': '',
            })
            return render(self.request, self.template_name, {'form': form})
        else:
            if Task.objects.filter(user=self.request.user, is_running=True).exists():
                messages.error(self.request, 'Задача уже выполняется. Подождите завершения.')
                form = SharesYFinanceForm(initial={
                    'symbol':  form.cleaned_data['symbol'],
                    'interval': form.cleaned_data['interval'],
                    'bound': form.cleaned_data['bound'],
                    'bound_unit': form.cleaned_data['bound_unit'],
                    'start_data': form.cleaned_data['start_data'],
                    'end_data': form.cleaned_data['end_data'],
                })
                return render(self.request, self.template_name, {'form': form})
            else:
                task = Task.objects.create(user=self.request.user, is_running=True)
                data = {
                    'symbol': symbol,
                    'interval': interval,
                    'bound_up': bound_up,
                    'bound_unit_up': bound_unit_up,
                    'bound_low': bound_low,
                    'bound_unit_low': bound_unit_low,
                    'start_data': start_data.strftime('%Y-%m-%d'),
                    'end_data': end_data.strftime('%Y-%m-%d'),
                    'us': self.request.user.id
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
                task = Task.objects.get(user=request.user, is_running=True)
                task.is_running = False
                task.save()
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
            if Task.objects.filter(user=self.request.user, is_running=True).exists():
                messages.error(self.request, 'Задача уже выполняется. Подождите завершения.')
                return redirect('shares_polygon')
            else:
                task = Task.objects.create(user=self.request.user, is_running=True)
                data = {
                    'symbol': symbol,
                    'interval': interval,
                    'bound': bound,
                    'bound_unit': bound_unit,
                    'start_date': str(start_data),
                    'end_date': str(end_data),
                    'file_for_big_bar': file_path_for_big_bar,
                    'file_for_small_bar': file_path_for_small_bar,
                    'us': self.request.user.id
                }

                task = tradingview_async_task.delay(data)
                request.session['task_id'] = task.id
                return redirect('process_shares')

        return render(request, self.template_name, {'form': form})


def template_polygon(request):
    templates = Template.objects.filter(name_exchange='Polygon', user_id=request.user.id)
    return render(request, 'template_polygon.html', {'templates': templates})


def delete_template_polygon(request, profile_id):
    teplate = Template.objects.get(pk=profile_id)
    if teplate.user == request.user:
        teplate.delete()
    return redirect('template_polygon')


def edit_template_polygon_view(request, profile_id):
    template_name = 'edit_template_polygon.html'
    template = get_object_or_404(Template, id=profile_id)

    if request.method == 'GET':
        print("GET method is executed")
        print(template.start_date)
        form = EditTemplatePolygonForm(initial={
            'name': template.name,
            'choice': template.choice,
            'symbol': template.symbol,
            'interval': template.interval,
            'bound_up': template.bound_up,
            'bound_unit_up': template.bound_unit_up,
            'bound_low': template.bound_low,
            'bound_unit_low': template.bound_unit_low,
            'custom_radio_field': template.min_interval,
            'start_data': datetime.strptime(template.start_date, '%Y-%m-%d %H:%M:%S'),
            'end_data': datetime.strptime(template.end_date, '%Y-%m-%d %H:%M:%S')
        })
        return render(request, template_name, {'form': form})

    elif request.method == 'POST':
        form = EditTemplatePolygonForm(request.POST)

        if form.is_valid():
            exist = Template.objects.filter(user=request.user.id, name_exchange='Polygon', name=form.cleaned_data['name'] ).exists()
            symbol_validity = check_symbol_validity(form.cleaned_data['symbol'], form.cleaned_data['start_data'], form.cleaned_data['end_data'])
            if symbol_validity == "invalid symbol":
                messages.error(request, 'Неверный символ!')
            elif float(form.cleaned_data['bound_up']) < 0:
                messages.error(request, 'Связка не может быть отрицательной!')
            elif float(form.cleaned_data['bound_low']) < 0:
                messages.error(request, 'Связка не может быть отрицательной!')
            elif form.cleaned_data['end_data'] < form.cleaned_data['start_data']:
                messages.error(request, 'Дата окончания должна быть позже даты начала!')
            elif exist:
                if get_object_or_404(Template, id=profile_id).name != form.cleaned_data['name']:
                    messages.error(request, 'Такое название шаблона уже существует!')
                    return redirect('edit_template_polygon', profile_id=profile_id)
                else:
                    template.name = form.cleaned_data['name']
                    template.choice = form.cleaned_data['choice']
                    template.symbol = form.cleaned_data['symbol']
                    template.interval = form.cleaned_data['interval']
                    template.bound_up = form.cleaned_data['bound_up']
                    template.bound_unit_up = form.cleaned_data['bound_unit_up']
                    template.bound_low = form.cleaned_data['bound_low']
                    template.bound_unit_low = form.cleaned_data['bound_unit_low']
                    template.start_date = form.cleaned_data['start_data']
                    template.end_date = form.cleaned_data['end_data']
                    template.min_interval = form.cleaned_data['custom_radio_field']
                    template.save()
                    return redirect('template_polygon')
            else:
                template.name = form.cleaned_data['name']
                template.choice = form.cleaned_data['choice']
                template.symbol = form.cleaned_data['symbol']
                template.interval = form.cleaned_data['interval']
                template.bound_up = form.cleaned_data['bound_up']
                template.bound_unit_up = form.cleaned_data['bound_unit_up']
                template.bound_low = form.cleaned_data['bound_low']
                template.bound_unit_low = form.cleaned_data['bound_unit_low']= form.cleaned_data['bound_unit']
                template.start_date = form.cleaned_data['start_data']
                template.end_date = form.cleaned_data['end_data']
                template.min_interval = form.cleaned_data['custom_radio_field']
                template.save()
                return redirect('template_polygon')

        return render(request, template_name, {'form': form})
    
    
def template_twelvedata(request):
    templates = Template.objects.filter(name_exchange='TwelveData', user_id=request.user.id)
    return render(request, 'template_twelvedata.html', {'templates': templates})


def delete_template_twelvedata(request, profile_id):
    teplate = Template.objects.get(pk=profile_id)
    if teplate.user == request.user:
        teplate.delete()
    return redirect('template_twelvedata')


class EditTemplateTwelveDataView(View):
    template_name = 'edit_template_twelvedata.html'

    def get(self, request, profile_id):
        template = get_object_or_404(Template, id=profile_id)
        interval_mapping = {
            '1 minute': '1min',
            '5 minute': '5min',
            '15 minute': '15min',
            '30 minute': '30min',
            '45 minute': '45min',
            '1 hour': '1h',
            '2 hour': '2h',
            '4 hour': '4h',
            '1 day': '1day',
            '1 week': '1week',
            '1 month': '1month'
        }
        form = EditTemplateTwelveDataForm(initial={
            'name': template.name,
            'symbol': template.symbol,
            'interval': interval_mapping[template.interval],
            'bound': template.bound,
            'bound_unit': template.bound_unit,
            'start_data': datetime.strptime(template.start_date, '%Y-%m-%d %H:%M:%S'),
            'end_data': datetime.strptime(template.end_date, '%Y-%m-%d %H:%M:%S')
        })
        return render(request, self.template_name, {'form': form})

    def post(self, request, profile_id):
        template = get_object_or_404(Template, id=profile_id)
        form = EditTemplateTwelveDataForm(request.POST)

        if form.is_valid():
            exist = Template.objects.filter(user=self.request.user.id, name_exchange='TwelveData', name=form.cleaned_data['name'] ).exists()
            symbol_validity = check_symbol_validity(form.cleaned_data['symbol'], form.cleaned_data['start_data'], form.cleaned_data['end_data'])
            if symbol_validity == "invalid symbol":
                messages.error(self.request, 'Неверный символ!')
                return redirect('edit_template_twelvedata', profile_id=profile_id)
            elif float(form.cleaned_data['bound']) < 0:
                messages.error(self.request, 'Связка не может быть отрицательной!')
                return redirect('edit_template_twelvedata', profile_id=profile_id)
            elif form.cleaned_data['end_data'] < form.cleaned_data['start_data']:
                messages.error(self.request, 'Дата окончания должна быть позже даты начала!')
                return redirect('edit_template_twelvedata', profile_id=profile_id)
            elif exist:
                if get_object_or_404(Template, id=profile_id).name != form.cleaned_data['name']:
                    messages.error(self.request, 'Такое название шаблона уже существует!')
                    return redirect('edit_template_twelvedata', profile_id=profile_id)
                else:
                    interval_mapping = {
                        '1min': '1 minute',
                        '5min': '5 minute',
                        '15min': '15 minute',
                        '30min': '30 minute',
                        '45min': '45 minute',
                        '1h': '1 hour',
                        '2h': '2 hour',
                        '4h': '4 hour',
                        '1day': '1 day',
                        '1week': '1 week',
                        '1month': '1 month'
                    }
                    template.name = form.cleaned_data['name']
                    template.symbol = form.cleaned_data['symbol']
                    template.interval = interval_mapping[form.cleaned_data['interval']]
                    template.bound = form.cleaned_data['bound']
                    template.bound_unit = form.cleaned_data['bound_unit']
                    template.start_date = form.cleaned_data['start_data']
                    template.end_date = form.cleaned_data['end_data']
                    template.min_interval = form.cleaned_data['custom_radio_field']
                    template.save()
                    return redirect('template_twelvedata')
            else:
                interval_mapping = {
                    '1min': '1 minute',
                    '5min': '5 minute',
                    '15min': '15 minute',
                    '30min': '30 minute',
                    '45min': '45 minute',
                    '1h': '1 hour',
                    '2h': '2 hour',
                    '4h': '4 hour',
                    '1day': '1 day',
                    '1week': '1 week',
                    '1month': '1 month'
                }
                template.name = form.cleaned_data['name']
                template.symbol = form.cleaned_data['symbol']
                template.interval = interval_mapping[form.cleaned_data['interval']]
                template.bound = form.cleaned_data['bound']
                template.bound_unit = form.cleaned_data['bound_unit']
                template.start_date = form.cleaned_data['start_data']
                template.end_date = form.cleaned_data['end_data']
                template.min_interval = form.cleaned_data['custom_radio_field']
                template.save()
                return redirect('template_twelvedata')

        return render(request, self.template_name, {'form': form})
    

def template_binance(request):
    templates = Template.objects.filter(name_exchange='Binance', user_id=request.user.id)
    return render(request, 'template_binance.html', {'templates': templates})


def delete_template_binance(request, profile_id):
    teplate = Template.objects.get(pk=profile_id)
    if teplate.user == request.user:
        teplate.delete()
    return redirect('template_binance')


class EditTemplateBinanceView(View):
    template_name = 'edit_template_binance.html'

    def get(self, request, profile_id):
        template = get_object_or_404(Template, id=profile_id)
        flipped_interval_mapping = {
                '1 minute': 0.0166666667,
                '3 minute': 0.05,
                '5 minute': 0.0833333333,
                '15 minute': 0.25,
                '30 minute': 0.5,
                '1 hour': 1,
                '2 hour': 2,
                '4 hour': 4,
                '6 hour': 6,
                '8 hour': 8,
                '12 hour': 12,
                '1 day': 24,
                '3 day': 72,
                '1 week': 168,
                '1 month': 720
            }
        form = EditTemplateBinancesForm(initial={
            'name': template.name,
            'symbol': template.symbol,
            'interval': flipped_interval_mapping[template.interval],
            'bound_up': template.bound_up,
            'bound_unit_up': template.bound_unit_up,
            'bound_low': template.bound_low,
            'bound_unit_low': template.bound_unit_low,
            'start_data': datetime.strptime(template.start_date, '%Y-%m-%d %H:%M:%S'),
            'end_data': datetime.strptime(template.end_date, '%Y-%m-%d %H:%M:%S'),
        })
        return render(request, self.template_name, {'form': form})

    def post(self, request, profile_id):
        template = get_object_or_404(Template, id=profile_id)
        form = EditTemplateBinancesForm(request.POST)

        if form.is_valid():
            exist = Template.objects.filter(user=self.request.user, name_exchange='Binance', name=form.cleaned_data['name'] ).exists()
            if form.cleaned_data['symbol'] not in get_binance_symbols():
                messages.error(self.request, 'Invalid symbol!')
                return redirect('edit_template_binance', profile_id=profile_id)
            elif float(form.cleaned_data['bound_up']) < 0:
                messages.error(self.request, 'Связка не может быть отрицательной!')
                return redirect('edit_template_binance', profile_id=profile_id)
            elif float(form.cleaned_data['bound_low']) < 0:
                messages.error(self.request, 'Связка не может быть отрицательной!')
                return redirect('edit_template_binance', profile_id=profile_id)
            elif form.cleaned_data['end_data'] < form.cleaned_data['start_data']:
                messages.error(self.request, 'Дата окончания должна быть позже даты начала!')
                return redirect('edit_template_binance', profile_id=profile_id)
            elif exist:
                if get_object_or_404(Template, id=profile_id).name != form.cleaned_data['name']:
                    messages.error(self.request, 'Такое название шаблона уже существует!')
                    return redirect('edit_template_binance', profile_id=profile_id)
                else:
                    interval_mapping = {
                        0.0166666667: '1 minute',
                        0.05: '3 minute',
                        0.0833333333: '5 minute',
                        0.25: '15 minute',
                        0.5: '30 minute',
                        1.0: '1 hour',
                        2.0: '2 hour',
                        4.0: '4 hour',
                        6.0: '6 hour',
                        8.0: '8 hour',
                        12.0: '12 hour',
                        24.0: '1 day',
                        72.0: '3 day',
                        168.0: '1 week',
                        720.0: '1 month'
                    }
                    template.name = form.cleaned_data['name']
                    template.symbol = form.cleaned_data['symbol']
                    template.interval = interval_mapping[float(form.cleaned_data['interval'])]
                    template.bound_up = form.cleaned_data['bound_up']
                    template.bound_unit_up = form.cleaned_data['bound_unit_up']
                    template.bound_low = form.cleaned_data['bound_low']
                    template.bound_unit_low = form.cleaned_data['bound_unit_low']
                    template.start_date = form.cleaned_data['start_data']
                    template.end_date = form.cleaned_data['end_data']
                    template.min_interval = form.cleaned_data['custom_radio_field']
                    template.save()
                    return redirect('template_binance')
            else:
                interval_mapping = {
                    0.0166666667: '1 minute',
                    0.05: '3 minute',
                    0.0833333333: '5 minute',
                    0.25: '15 minute',
                    0.5: '30 minute',
                    1.0: '1 hour',
                    2.0: '2 hour',
                    4.0: '4 hour',
                    6.0: '6 hour',
                    8.0: '8 hour',
                    12.0: '12 hour',
                    24.0: '1 day',
                    72.0: '3 day',
                    168.0: '1 week',
                    720.0: '1 month'
                }
                template.name = form.cleaned_data['name']
                template.symbol = form.cleaned_data['symbol']
                template.interval = interval_mapping[float(form.cleaned_data['interval'])]
                template.bound_up = form.cleaned_data['bound_up']
                template.bound_unit_up = form.cleaned_data['bound_unit_up']
                template.bound_low = form.cleaned_data['bound_low']
                template.bound_unit_low = form.cleaned_data['bound_unit_low']
                template.start_date = form.cleaned_data['start_data']
                template.end_date = form.cleaned_data['end_data']
                template.min_interval = form.cleaned_data['custom_radio_field']
                template.save()
                return redirect('template_binance')

        return render(request, self.template_name, {'form': form})