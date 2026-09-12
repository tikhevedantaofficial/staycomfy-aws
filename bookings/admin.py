from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'hotel', 'room', 'check_in', 'check_out', 'guests', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'hotel', 'created_at')
    search_fields = ('user__email', 'hotel__name', 'room__name')
    ordering = ('-created_at',)
    list_editable = ('status',)
