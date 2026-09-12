from django.urls import path
from . import views

urlpatterns = [
    path('hotels/<int:hotel_pk>/rooms/<int:room_pk>/book/', views.create_booking, name='create_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
]
