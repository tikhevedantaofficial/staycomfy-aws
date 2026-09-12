from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import Hotel, Room


def home(request):
    hotels = Hotel.objects.all()
    return render(request, 'home.html', {'hotels': hotels})


def hotel_detail(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    rooms = hotel.rooms.all()
    return render(request, 'hotels/detail.html', {'hotel': hotel, 'rooms': rooms})
