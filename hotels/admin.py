from django.contrib import admin
from .models import Hotel, Room


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'rating', 'created_at')
    list_filter = ('city', 'rating')
    search_fields = ('name', 'city', 'description')
    ordering = ('-created_at',)
    inlines = [RoomInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'price_per_night', 'capacity')
    list_filter = ('hotel',)
    search_fields = ('name', 'hotel__name')
    ordering = ('hotel', 'price_per_night')
