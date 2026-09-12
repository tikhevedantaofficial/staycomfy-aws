from django import forms
from django.utils import timezone

from hotels.models import Room
from .models import Booking


class BookingCreateForm(forms.Form):
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

    def __init__(self, *args, room=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.room = room

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        guests = cleaned_data.get('guests')

        if not all([check_in, check_out, guests]):
            return cleaned_data

        today = timezone.now().date()
        if check_in < today:
            self.add_error('check_in', 'Check-in date cannot be in the past.')

        if check_out <= check_in:
            self.add_error('check_out', 'Check-out date must be after check-in date.')

        if guests < 1:
            self.add_error('guests', 'Number of guests must be at least 1.')

        if self.room and guests > self.room.capacity:
            self.add_error('guests', f'This room can accommodate a maximum of {self.room.capacity} guests.')

        # Check for overlapping confirmed bookings
        if self.room and check_in and check_out and check_out > check_in:
            overlapping = Booking.objects.filter(
                room=self.room,
                status='confirmed',
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            if overlapping.exists():
                self.add_error(None, 'This room is not available for the selected dates. Please choose different dates.')

        return cleaned_data
