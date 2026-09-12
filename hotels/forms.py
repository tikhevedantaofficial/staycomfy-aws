from django import forms


class BookingForm(forms.Form):
    check_in = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control glass-input',
    }))
    check_out = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control glass-input',
    }))
    guests = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={
        'min': 1,
        'class': 'form-control glass-input',
    }))
