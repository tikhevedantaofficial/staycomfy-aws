from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from hotels.models import Hotel, Room
from .models import Booking
from .forms import BookingCreateForm


@login_required
def create_booking(request, hotel_pk, room_pk):
    hotel = get_object_or_404(Hotel, pk=hotel_pk)
    room = get_object_or_404(Room, pk=room_pk, hotel=hotel)

    if request.method == 'POST':
        form = BookingCreateForm(request.POST, room=room)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            guests = form.cleaned_data['guests']
            nights = (check_out - check_in).days
            total_price = Decimal(nights) * room.price_per_night

            Booking.objects.create(
                user=request.user,
                hotel=hotel,
                room=room,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
                total_price=total_price,
                status='confirmed',
            )
            messages.success(request, 'Your booking has been confirmed!')
            return redirect('my_bookings')
    else:
        # Default dates: tomorrow to day after
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        day_after = timezone.now().date() + timezone.timedelta(days=2)
        form = BookingCreateForm(initial={
            'check_in': tomorrow,
            'check_out': day_after,
            'guests': 1,
        }, room=room)

    nights = 1
    total_price = room.price_per_night
    if form.is_bound and form.is_valid():
        ci = form.cleaned_data['check_in']
        co = form.cleaned_data['check_out']
        nights = (co - ci).days
        total_price = Decimal(nights) * room.price_per_night

    return render(request, 'bookings/create.html', {
        'form': form,
        'hotel': hotel,
        'room': room,
        'nights': nights,
        'total_price': total_price,
    })


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).exclude(status='cancelled').select_related('hotel', 'room')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if booking.user != request.user:
        messages.error(request, 'You are not authorized to cancel this booking.')
        return redirect('my_bookings')

    if request.method == 'POST':
        if booking.can_cancel:
            booking.status = 'cancelled'
            booking.save(update_fields=['status'])
            messages.success(request, 'Your booking has been cancelled.')
        else:
            messages.warning(request, 'This booking cannot be cancelled.')

    return redirect('my_bookings')
