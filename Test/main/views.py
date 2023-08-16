from django.shortcuts import render, redirect
from .forms import MyForm, SharesForm
from .tasks import process_data_async, shared_async_task
from celery.result import AsyncResult
from django.http import JsonResponse
from django.http import HttpResponse
import os

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
            data = {
                'symbol': symbol,
                'interval': interval,
                'bound': bound,
                'bound_unit': bound_unit,
                'start_data': start_data,
                'end_data': end_data
            }
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
            data = {
                'symbol': symbol,
                'interval': interval,
                'bound': bound,
                'bound_unit': bound_unit,
                'start_data': start_data,
                'end_data': end_data
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