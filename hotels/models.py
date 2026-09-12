from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.city}"

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        # Placeholder gradient fallback
        return ''


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=150)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.PositiveIntegerField(default=2)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)

    class Meta:
        ordering = ['price_per_night']

    def __str__(self):
        return f"{self.name} @ {self.hotel.name}"

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return ''
