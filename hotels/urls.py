from django.urls import path
from . import views

urlpatterns = [
    path('hotels/<int:pk>/', views.hotel_detail, name='hotel_detail'),
]
