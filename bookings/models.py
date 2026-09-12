from django.db import models
from django.conf import settings


class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey('hotels.Hotel', on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey('hotels.Room', on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    welcome_email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['room', 'check_in', 'check_out']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['check_in', 'welcome_email_sent']),
        ]

    def __str__(self):
        return f"{self.user.email} — {self.room.name} @ {self.hotel.name}"

    @property
    def num_nights(self):
        return (self.check_out - self.check_in).days

    @property
    def can_cancel(self):
        return self.status == 'confirmed'
    
    @property
    def user_email(self):
        return self.user.email
