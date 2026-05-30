"""Watercraft models."""
from django.db import models
from django.core.validators import MinValueValidator


class Watercraft(models.Model):
    class Type(models.TextChoices):
        BOAT = 'boat', 'Boat'
        JET_SKI = 'jet_ski', 'Jet Ski'
        YACHT = 'yacht', 'Yacht'
        SPEED_BOAT = 'speed_boat', 'Speed Boat'

    name = models.CharField(max_length=120)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.BOAT)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='watercraft/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text="Optional external image URL fallback")
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    passenger_capacity = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    location = models.CharField(max_length=200, blank=True, help_text="Dock or marina location")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    def get_display_image(self):
        if self.image:
            return self.image.url
        return self.image_url or ''
