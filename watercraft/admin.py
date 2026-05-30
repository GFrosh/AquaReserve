from django.contrib import admin
from .models import Watercraft


@admin.register(Watercraft)
class WatercraftAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'price_per_hour', 'passenger_capacity', 'is_available')
    list_filter = ('type', 'is_available')
    search_fields = ('name', 'description', 'location')
    list_editable = ('is_available', 'price_per_hour')
