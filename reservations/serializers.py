from datetime import datetime, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from watercraft.models import Watercraft
from watercraft.serializers import WatercraftSerializer
from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    watercraft_detail = WatercraftSerializer(source='watercraft', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    duration_hours = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'user', 'user_username',
            'watercraft', 'watercraft_detail',
            'reservation_date', 'start_time', 'end_time',
            'passenger_count', 'total_price',
            'status', 'status_display', 'notes',
            'duration_hours',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'total_price', 'status', 'created_at', 'updated_at']

    def get_duration_hours(self, obj):
        try:
            return float(obj.duration_hours)
        except Exception:
            return 0

    def validate(self, attrs):
        # Build a temp instance to leverage model.clean()
        instance = Reservation(
            user=self.context['request'].user if self.instance is None else self.instance.user,
            watercraft=attrs.get('watercraft', getattr(self.instance, 'watercraft', None)),
            reservation_date=attrs.get('reservation_date', getattr(self.instance, 'reservation_date', None)),
            start_time=attrs.get('start_time', getattr(self.instance, 'start_time', None)),
            end_time=attrs.get('end_time', getattr(self.instance, 'end_time', None)),
            passenger_count=attrs.get('passenger_count', getattr(self.instance, 'passenger_count', 1)),
            status=getattr(self.instance, 'status', Reservation.Status.PENDING),
        )
        if self.instance:
            instance.pk = self.instance.pk
        try:
            instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages})
        return attrs


class AdminReservationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['status']

    def validate_status(self, value):
        if value not in dict(Reservation.Status.choices):
            raise serializers.ValidationError("Invalid status.")
        return value
