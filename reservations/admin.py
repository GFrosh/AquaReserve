from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'watercraft', 'reservation_date',
                    'start_time', 'end_time', 'status', 'total_price')
    list_filter = ('status', 'reservation_date', 'watercraft__type')
    search_fields = ('user__username', 'watercraft__name')
    date_hierarchy = 'reservation_date'
    list_editable = ('status',)
