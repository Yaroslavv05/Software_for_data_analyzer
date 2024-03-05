from django import forms
from .models import UserProfiles, Template
from django.forms.widgets import MultiWidget, TextInput
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from binance.client import Client
import datetime
from django.db.models import Q


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
    def __init__(self, user, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        
        templates = Template.objects.filter(Q(user=user) & Q(name_exchange='Binance'))
        ACCOUNT_CHOICES = [(template.id, template.name) for template in templates]
        
        self.fields['selected_template'] = forms.ChoiceField(
            required=False,
            choices=ACCOUNT_CHOICES,
            widget=forms.Select(attrs={'class': 'form-select mb-2'})
        )
        
        self.has_templates = bool(ACCOUNT_CHOICES)
        
    symbol = forms.ChoiceField(required=False, choices=sorted_symbols, widget=forms.Select(attrs={'class': 'form-control mb-2'}))
    interval = forms.ChoiceField(choices=(
        (0.0166666667, '1м'), (0.05, '3м'), (0.0833333333, '5м'), (0.25, '15м'), (0.5, '30м'), (1, '1ч'), (2, '2ч'),
        (4, '4ч'),
        (6, '6ч'), (8, '8ч'), (12, '12ч'), (24, '1д'), (72, '3д'), (168, '1н'), (720, '1М'),
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    BOUND_UNIT_CHOICES = [
        ('$', 'Доллар ($)'),
        ('%', 'Процент (%)'),
    ]
    bound_up = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел верх'}))
    bound_unit_up = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    bound_low = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел низ'}))
    bound_unit_low = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = SplitDateTimeField(required=False)
    end_data = SplitDateTimeField(required=False)
    save_tamplates = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    use_template = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': "checkbox", "id": "use-template", 'name': "use_template"}))
    custom_radio_field = forms.ChoiceField(
        choices=(
            ('60', '1 минута'),
        ), 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )


class BinanceNewForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(BinanceNewForm, self).__init__(*args, **kwargs)
        
        templates = Template.objects.filter(Q(user=user) & Q(name_exchange='Binance'))
        ACCOUNT_CHOICES = [(template.id, template.name) for template in templates]
        
        self.fields['selected_template'] = forms.ChoiceField(
            required=False,
            choices=ACCOUNT_CHOICES,
            widget=forms.Select(attrs={'class': 'form-select mb-2'})
        )
        
        self.has_templates = bool(ACCOUNT_CHOICES)
        
    symbol = forms.ChoiceField(required=False, choices=sorted_symbols, widget=forms.Select(attrs={'class': 'form-control mb-2'}))
    interval = forms.ChoiceField(choices=(
        (0.0166666667, '1м'), (0.05, '3м'), (0.0833333333, '5м'), (0.25, '15м'), (0.5, '30м'), (1, '1ч'), (2, '2ч'),
        (4, '4ч'),
        (6, '6ч'), (8, '8ч'), (12, '12ч'), (24, '1д'), (72, '3д'), (168, '1н'), (720, '1М'),
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = SplitDateTimeField(required=False)
    end_data = SplitDateTimeField(required=False)
    interval_start = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Начало интервала'}))
    interval_end = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Конец интервала'}))
    # save_tamplates = forms.BooleanField(
    #     required=False,
    #     widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    # use_template = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': "checkbox", "id": "use-template", 'name': "use_template"}))
    custom_radio_field = forms.ChoiceField(
        choices=(
            ('60', '1 минута'),
        ), 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    

class SharesForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(SharesForm, self).__init__(*args, **kwargs)
        
        templates = Template.objects.filter(Q(user=user) & Q(name_exchange='TwelveData'))
        ACCOUNT_CHOICES = [(template.id, template.name) for template in templates]
        
        self.fields['selected_template'] = forms.ChoiceField(
            required=False,
            choices=ACCOUNT_CHOICES,
            widget=forms.Select(attrs={'class': 'form-select mb-2'})
        )
        
        self.has_templates = bool(ACCOUNT_CHOICES)

    symbol = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Cимвол'}))
    interval = forms.ChoiceField(choices=(
        ('1min', '1м'), ('5min', '5м'), ('15min', '15м'), ('30min', '30м'), ('45min', '45м'), ('1h', '1ч'), ('2h', '2ч'), ('4h', '4ч'),
        ('1day', '1д'), ('1week', '1н'), ('1month', '1М')
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    BOUND_UNIT_CHOICES = [
        ('$', 'Доллар ($)'),
        ('%', 'Процент (%)'),
    ]
    bound_up = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел верх'}))
    bound_unit_up = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    bound_low = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел низ'}))
    bound_unit_low = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = SplitDateTimeField(required=False)
    end_data = SplitDateTimeField(required=False)
    save_tamplates = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    use_template = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': "checkbox", "id": "use-template", 'name': "use_template"}))
    custom_radio_field = forms.ChoiceField(
        choices=(
            ('60', '1 минута'),
        ), 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )



class SharesPolygonForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(SharesPolygonForm, self).__init__(*args, **kwargs)
        
        templates = Template.objects.filter(Q(user=user) & Q(name_exchange='Polygon'))
        ACCOUNT_CHOICES = [(template.id, template.name) for template in templates]
        
        self.fields['selected_template'] = forms.ChoiceField(
            required=False,
            choices=ACCOUNT_CHOICES,
            widget=forms.Select(attrs={'class': 'form-select mb-2'})
        )

        self.has_templates = bool(ACCOUNT_CHOICES)
          
    choice = forms.ChoiceField(choices=(
        ('pre', 'PRE данные'),
        ('in', 'IN данные'),
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    symbol = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Cимвол'}))
    interval = forms.ChoiceField(choices=(
        ('1 minute', '1м'), ('5 minute', '5м'), ('15 minute', '15м'), ('30 minute', '30м'), ('45 minute', '45м'), ('1 hour', '1ч'), ('2 hour', '2ч'), ('3 hour', '3ч'), ('4 hour', '4ч'),
        ('5 hour', '5ч'), ('6 hour', '6ч'), ('7 hour', '7ч'), ('8 hour', '8ч'), ('9 hour', '9ч'), ('10 hour', '10ч'), ('11 hour', '11ч'), ('12 hour', '12ч'), ('1 day', '1д'), ('1 week', '1н'),
        ('1 month', '1М'), ('1 year', '1г')
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    BOUND_UNIT_CHOICES = [
        ('$', 'Доллар ($)'),
        ('%', 'Процент (%)'),
    ]
    bound_up = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел верх'}))
    bound_unit_up = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    bound_low = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел низ'}))
    bound_unit_low = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = SplitDateTimeField(required=False)
    end_data = SplitDateTimeField(required=False )
    save_tamplates = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    use_template = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': "checkbox", "id": "use-template", 'name': "use_template"}))
    custom_radio_field = forms.ChoiceField(
        choices=(
            ('60', '1 минута'),
        ), 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=False
    )


class SharesPolygonNewForm(forms.Form):          
    choice = forms.ChoiceField(choices=(
        ('pre', 'PRE данные'),
        ('in', 'IN данные'),
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    symbol = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Cимвол'}))
    interval = forms.ChoiceField(choices=(
        ('1 minute', '1м'), ('5 minute', '5м'), ('15 minute', '15м'), ('30 minute', '30м'), ('45 minute', '45м'), ('1 hour', '1ч'), ('2 hour', '2ч'), ('3 hour', '3ч'), ('4 hour', '4ч'),
        ('5 hour', '5ч'), ('6 hour', '6ч'), ('7 hour', '7ч'), ('8 hour', '8ч'), ('9 hour', '9ч'), ('10 hour', '10ч'), ('11 hour', '11ч'), ('12 hour', '12ч'), ('1 day', '1д'), ('1 week', '1н'),
        ('1 month', '1М'), ('1 year', '1г')
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    interval_start = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Начало интервала'}))
    interval_end = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Конец интервала'}))
    start_data = SplitDateTimeField(required=False)
    end_data = SplitDateTimeField(required=False )
    custom_radio_field = forms.ChoiceField(
        choices=(
            ('60', '1 минута'),
        ), 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=False
    )


class SharesYFinanceForm(forms.Form):
    symbol = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Cимвол'}))
    interval = forms.ChoiceField(choices=(
        ('1m', '1м'), ('2m', '2м'), ('5m', '5м'), ('15m', '15м'), ('30m', '30м'), ('1h', '1ч'), ('90m', '1.5ч'), ('1d', '1д'), ('5d', '5д'),
        ('1wk', '1н'), ('1mo', '1М'), ('3mo', '3М')
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    BOUND_UNIT_CHOICES = [ 
        ('$', 'Доллар ($)'),
        ('%', 'Процент (%)'),
    ]
    bound_up = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел верх'}))
    bound_unit_up = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    bound_low = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел низ'}))
    bound_unit_low = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = SplitDateTimeField()
    end_data = SplitDateTimeField()
    custom_radio_field = forms.ChoiceField(
        choices=(
            ('60', '1 минута'),
        ), 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя:", widget=forms.TextInput(attrs={'type': 'email', 'name': 'email', 'placeholder': 'Почта'}))
    password = forms.CharField(label="Пароль:", widget=forms.PasswordInput(attrs={'type': 'password', 'name': 'password', 'placeholder': 'Пароль'}))


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'type': 'password', 'name': 'password', 'placeholder': 'Старый пароль'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'type': 'password', 'name': 'password', 'placeholder': 'Новый пароль'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'type': 'password', 'name': 'password', 'placeholder': 'Повторите новый пароль'}))


class FirstNameChangeForm(forms.Form):
    new_nickname = forms.CharField(widget=forms.TextInput(attrs={'type': 'text', 'name': 'username', 'placeholder': 'Новое имя'}))


class AccountBinanceForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Название'}))
    api_key = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Api ключ'}))
    secret_key = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Secret ключ'}))


class TradingForm(forms.Form):
    def __init__(self, user_id, *args, **kwargs):
        super(TradingForm, self).__init__(*args, **kwargs)

        user_profiles = UserProfiles.objects.filter(user_id=user_id)
        ACCOUNT_CHOICES = [(profile.id, profile.name) for profile in user_profiles]

        self.fields['account'] = forms.ChoiceField(
            choices=ACCOUNT_CHOICES,
            widget=forms.Select(attrs={'class': 'form-select mb-2'})
        )

    uploaded_file = forms.CharField(widget=forms.FileInput(attrs={'class': 'form-control mb-2'}))
    crypto_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Название'}))
    usdt_amount = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Кол-во USDT'}))
    leverage = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Кредитное плече'}))


class TradingviewForm(forms.Form):
    symbol = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Символ'}))
    interval = forms.ChoiceField(choices=(
        ('1m', '1м'), ('3m', '3м'), ('5m', '5м'), ('15m', '15м'), ('30m', '30м'), ('45m', '45м'), ('1h', '1ч'), ('2h', '2ч'), ('3h', '3ч'), ('4h', '4ч'),
        ('1d', '1д'), ('1wk', '1н'), ('1mo', '1М'), ('3mo', '3М'), ('6mo', '6М'), ('12mo', '12М')
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    BOUND_UNIT_CHOICES = [
        ('$', 'Доллар ($)'),
        ('%', 'Процент (%)'),
    ]
    bound = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел'}))
    bound_unit = forms.ChoiceField(choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = SplitDateTimeField()
    end_data = SplitDateTimeField()
    file_for_big_bar = forms.CharField(widget=forms.FileInput(attrs={'class': 'form-control mb-2'}))
    file_for_small_bar = forms.CharField(widget=forms.FileInput(attrs={'class': 'form-control mb-2'}))


class EditTemplatePolygonForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Название'}))
    choice = forms.ChoiceField(choices=(
        ('pre', 'PRE данные'),
        ('in', 'IN данные'),
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
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
    bound_up = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел верх'}))
    bound_unit_up = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    bound_low = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел низ'}))
    bound_unit_low = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = SplitDateTimeField()
    end_data = SplitDateTimeField()
    custom_radio_field = forms.ChoiceField(
        choices=(
            ('60', '1 минута'),
        ), 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )


class EditTemplateTwelveDataForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Название'}))
    symbol = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Cимвол'}))
    interval = forms.ChoiceField(choices=(
        ('1min', '1м'), ('5min', '5м'), ('15min', '15м'), ('30min', '30м'), ('45min', '45м'), ('1h', '1ч'), ('2h', '2ч'), ('4h', '4ч'),
        ('1day', '1д'), ('1week', '1н'), ('1month', '1М')
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    BOUND_UNIT_CHOICES = [
        ('$', 'Доллар ($)'),
        ('%', 'Процент (%)'),
    ]
    bound_up = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел верх'}))
    bound_unit_up = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    bound_low = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел низ'}))
    bound_unit_low = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = SplitDateTimeField()
    end_data = SplitDateTimeField()
    custom_radio_field = forms.ChoiceField(
        choices=(
            ('60', '1 минута'),
        ), 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )


class EditTemplateBinancesForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Название'}))
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
    bound_up = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел верх'}))
    bound_unit_up = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    bound_low = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Предел низ'}))
    bound_unit_low = forms.ChoiceField(required=False, choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = SplitDateTimeField()
    end_data = SplitDateTimeField()
    custom_radio_field = forms.ChoiceField(
        choices=(
            ('60', '1 минута'),
        ), 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )