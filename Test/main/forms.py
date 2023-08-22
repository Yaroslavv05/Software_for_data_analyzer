from django import forms
from django.forms.widgets import MultiWidget, TextInput
from django.utils.safestring import mark_safe
from binance.client import Client
import datetime


class SplitDateTimeWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            TextInput(attrs={'type': 'date', 'class': 'form-control mb-2'}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.date(), value.strftime('%H'), value.strftime('%M')]
        return [None, None, None]

    def format_output(self, rendered_widgets):
        labels = ['Start Date' 'End Date']
        rendered_with_labels = [f'<div class="splitdatetime-label">{label}</div>{widget}' for label, widget in zip(labels, rendered_widgets)]
        return mark_safe('<div class="splitdatetime">%s</div>' % ' '.join(rendered_with_labels))


class SplitDateTimeField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (
            forms.DateField(),
        )
        super().__init__(fields, *args, **kwargs)
        self.widget = SplitDateTimeWidget()

    def compress(self, values):
        if values:
            date_value = values[0]
            return datetime.datetime(date_value.year, date_value.month, date_value.day)
        return None


client = Client()
exchange_info = client.futures_exchange_info()
symbols = exchange_info['symbols']
futures_symbols = [(symbol['symbol'], symbol['symbol']) for symbol in symbols if symbol['contractType'] == 'PERPETUAL']
sorted_symbols = sorted(futures_symbols, key=lambda x: x[0])


class MyForm(forms.Form):
    symbol = forms.ChoiceField(choices=sorted_symbols, widget=forms.Select(attrs={'class': 'form-control mb-2'}))
    interval = forms.ChoiceField(choices=(
        (0.0166666667, '1м'), (0.05, '3м'), (0.0833333333, '5м'), (0.25, '15м'), (0.5, '30м'), (1, '1ч'), (2, '2ч'),
        (4, '4ч'),
        (6, '6ч'), (8, '8ч'), (12, '12ч'), (24, '1д'), (72, '3д'), (168, '1н'), (720, '1М'),
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    BOUND_UNIT_CHOICES = [
        ('$', 'Доллар ($)'),
        ('%', 'Процент (%)'),
    ]
    bound = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел'}))
    bound_unit = forms.ChoiceField(choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = SplitDateTimeField()
    end_data = SplitDateTimeField()


class SharesForm(forms.Form):
    symbol = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Cимвол'}))
    interval = forms.ChoiceField(choices=(
        ('1min', '1м'), ('5min', '5м'), ('15min', '15м'), ('30min', '30м'), ('45min', '45м'), ('1h', '1ч'), ('2h', '2ч'), ('4h', '4ч'),
        ('1day', '1д'), ('1week', '1н'), ('1month', '1М')
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    BOUND_UNIT_CHOICES = [
        ('$', 'Доллар ($)'),
        ('%', 'Процент (%)'),
    ]
    bound = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел'}))
    bound_unit = forms.ChoiceField(choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = SplitDateTimeField()
    end_data = SplitDateTimeField()


class SharesPolygonForm(forms.Form):
    symbol = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Cимвол'}))
    interval = forms.ChoiceField(choices=(
        ('1 minute', '1м'), ('5 minute', '5м'), ('15 minute', '15м'), ('30 minute', '30м'), ('45 minute', '45м'), ('1 hour', '1ч'), ('2 hour', '2ч'), ('3 hour', '3ч'), ('4 hour', '4ч'),
        ('5 hour', '5ч'), ('6 hour', '6ч'), ('7 hour', '7ч'), ('8 hour', '8ч'), ('9 hour', '9ч'), ('10 hour', '10ч'), ('11 hour', '11ч'), ('12 hour', '12ч'), ('1 day', '1д'), ('1 week', '1н'),
        ('1 month', '1М'), ('1 year', '1г')
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    BOUND_UNIT_CHOICES = [
        ('$', 'Доллар ($)'),
        ('%', 'Процент (%)'),
    ]
    bound = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел'}))
    bound_unit = forms.ChoiceField(choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = SplitDateTimeField()
    end_data = SplitDateTimeField()