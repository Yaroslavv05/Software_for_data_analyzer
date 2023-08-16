from django import forms


class MyForm(forms.Form):
    symbol = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Symbol'}))
    interval = forms.ChoiceField(choices=(
        (0.0166666667, '1м'), (0.05, '3м'), (0.0833333333, '5м'), (0.25, '15м'), (0.5, '30м'), (1, '1ч'), (2, '2ч'),
        (4, '4ч'),
        (6, '6ч'), (8, '8ч'), (12, '12ч'), (24, '1д'), (72, '3д'), (168, '1н'), (720, '1М'),
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    BOUND_UNIT_CHOICES = [
        ('$', 'Dollars ($)'),
        ('%', 'Percentage (%)'),
    ]
    bound = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Bound'}))
    bound_unit = forms.ChoiceField(choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Start data'}))
    end_data = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'End data'}))


class SharesForm(forms.Form):
    symbol = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Symbol'}))
    interval = forms.ChoiceField(choices=(
        ('1min', '1м'), ('5min', '5м'), ('15min', '15м'), ('30min', '30м'), ('45min', '45м'), ('1h', '1ч'), ('2h', '2ч'), ('4h', '4ч'),
        ('1day', '1д'), ('1week', '1н'), ('1month', '1М')
    ), widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    BOUND_UNIT_CHOICES = [
        ('$', 'Dollars ($)'),
        ('%', 'Percentage (%)'),
    ]
    bound = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Bound'}))
    bound_unit = forms.ChoiceField(choices=BOUND_UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-2'}))
    start_data = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Start data'}))
    end_data = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'End data'}))
