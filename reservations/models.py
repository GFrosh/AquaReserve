"""Reservation models with overlap-prevention business logic."""
from decimal import Decimal
from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from watercraft.models import Watercraft


class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    watercraft = models.ForeignKey(Watercraft, on_delete=models.CASCADE, related_name='reservations')

    reservation_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    passenger_count = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reservation_date', '-start_time']

    def __str__(self):
        return f"{self.watercraft.name} | {self.user.username} | {self.reservation_date} {self.start_time}-{self.end_time}"

    # ----- Business logic helpers -----

    @property
    def start_datetime(self):
        return timezone.make_aware(datetime.combine(self.reservation_date, self.start_time)) \
            if timezone.is_naive(datetime.combine(self.reservation_date, self.start_time)) \
            else datetime.combine(self.reservation_date, self.start_time)

    @property
    def end_datetime(self):
        return timezone.make_aware(datetime.combine(self.reservation_date, self.end_time)) \
            if timezone.is_naive(datetime.combine(self.reservation_date, self.end_time)) \
            else datetime.combine(self.reservation_date, self.end_time)

    @property
    def duration_hours(self) -> Decimal:
        start_dt = datetime.combine(self.reservation_date, self.start_time)
        end_dt = datetime.combine(self.reservation_date, self.end_time)
        delta: timedelta = end_dt - start_dt
        return Decimal(delta.total_seconds()) / Decimal(3600)

    def calculate_total_price(self) -> Decimal:
        return (self.duration_hours * self.watercraft.price_per_hour).quantize(Decimal('0.01'))

    def overlaps_with_existing(self) -> bool:
        """Return True if this reservation overlaps with another active booking
        for the same watercraft."""
        blocking_statuses = [self.Status.PENDING, self.Status.APPROVED]
        qs = Reservation.objects.filter(
            watercraft=self.watercraft,
            reservation_date=self.reservation_date,
            status__in=blocking_statuses,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        # Standard interval overlap check: existing.start < new.end AND existing.end > new.start
        qs = qs.filter(start_time__lt=self.end_time, end_time__gt=self.start_time)
        return qs.exists()

    def clean(self):
        errors = {}

        # 1. Time order
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            errors['end_time'] = 'End time must be after start time.'

        # 2. Duration must be at least 30 minutes
        if self.start_time and self.end_time and self.reservation_date:
            duration = datetime.combine(self.reservation_date, self.end_time) - \
                       datetime.combine(self.reservation_date, self.start_time)
            if duration < timedelta(minutes=30):
                errors['end_time'] = 'Reservation must be at least 30 minutes long.'
            if duration > timedelta(hours=12):
                errors['end_time'] = 'Reservation cannot exceed 12 hours.'

        # 3. No past bookings
        if self.reservation_date and self.start_time:
            booking_dt = datetime.combine(self.reservation_date, self.start_time)
            now = timezone.now().replace(tzinfo=None) if timezone.is_aware(timezone.now()) else timezone.now()
            # Use naive comparison since reservation fields are naive date/time
            now_naive = datetime.utcnow()
            if booking_dt < now_naive:
                errors['reservation_date'] = 'Cannot book a slot in the past.'

        # 4. Watercraft must exist and be available
        if self.watercraft_id:
            if not self.watercraft.is_available:
                errors['watercraft'] = 'This watercraft is currently unavailable.'
            # 5. Capacity check
            if self.passenger_count and self.passenger_count > self.watercraft.passenger_capacity:
                errors['passenger_count'] = (
                    f'Passenger count exceeds capacity '
                    f'({self.watercraft.passenger_capacity}).'
                )
            if self.passenger_count is not None and self.passenger_count < 1:
                errors['passenger_count'] = 'At least one passenger is required.'

        # 6. Overlap check
        if self.watercraft_id and self.reservation_date and self.start_time and self.end_time \
                and self.status in [self.Status.PENDING, self.Status.APPROVED]:
            if self.overlaps_with_existing():
                errors['start_time'] = 'This time slot overlaps with an existing reservation.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # auto-compute price
        if self.watercraft_id and self.reservation_date and self.start_time and self.end_time:
            self.total_price = self.calculate_total_price()
        self.full_clean()
        super().save(*args, **kwargs)
