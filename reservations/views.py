from django.db.models import Count, Sum, Q
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import Reservation
from .serializers import ReservationSerializer, AdminReservationStatusSerializer
from .permissions import IsOwnerOrAdmin, IsAdminUserRole
from watercraft.models import Watercraft


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = Reservation.objects.select_related('watercraft', 'user').all()
        # Customers only see their own; admins see all
        if not (getattr(user, 'is_admin_role', False) or user.is_staff):
            qs = qs.filter(user=user)
        # filters
        status_param = self.request.query_params.get('status')
        watercraft_id = self.request.query_params.get('watercraft')
        date_param = self.request.query_params.get('date')
        if status_param:
            qs = qs.filter(status=status_param)
        if watercraft_id:
            qs = qs.filter(watercraft_id=watercraft_id)
        if date_param:
            qs = qs.filter(reservation_date=date_param)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status=Reservation.Status.PENDING)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrAdmin])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status in [Reservation.Status.COMPLETED, Reservation.Status.CANCELLED]:
            return Response({'detail': f'Cannot cancel a {reservation.status} reservation.'},
                            status=status.HTTP_400_BAD_REQUEST)
        reservation.status = Reservation.Status.CANCELLED
        reservation.save()
        return Response(ReservationSerializer(reservation, context={'request': request}).data)


# --- Admin endpoints ---

@api_view(['GET'])
@permission_classes([IsAdminUserRole])
def admin_reservations(request):
    qs = Reservation.objects.select_related('watercraft', 'user').all().order_by('-created_at')
    status_param = request.query_params.get('status')
    if status_param:
        qs = qs.filter(status=status_param)
    serializer = ReservationSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAdminUserRole])
def admin_update_status(request, pk):
    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=404)
    serializer = AdminReservationStatusSerializer(reservation, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    reservation.status = serializer.validated_data['status']
    # Bypass full_clean overlap check when admin is just changing status (e.g. rejecting/completing)
    reservation.save(update_fields=['status', 'updated_at']) if False else reservation.save()
    return Response(ReservationSerializer(reservation, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([IsAdminUserRole])
def admin_stats(request):
    total = Reservation.objects.count()
    pending = Reservation.objects.filter(status=Reservation.Status.PENDING).count()
    approved = Reservation.objects.filter(status=Reservation.Status.APPROVED).count()
    cancelled = Reservation.objects.filter(status=Reservation.Status.CANCELLED).count()
    revenue = Reservation.objects.filter(
        status__in=[Reservation.Status.APPROVED, Reservation.Status.COMPLETED]
    ).aggregate(total=Sum('total_price'))['total'] or 0
    watercraft_total = Watercraft.objects.count()
    watercraft_available = Watercraft.objects.filter(is_available=True).count()

    today = timezone.now().date()
    today_bookings = Reservation.objects.filter(reservation_date=today).count()

    top_watercraft = list(
        Reservation.objects.values('watercraft__name', 'watercraft__type')
        .annotate(bookings=Count('id'))
        .order_by('-bookings')[:5]
    )

    return Response({
        'totals': {
            'reservations': total,
            'pending': pending,
            'approved': approved,
            'cancelled': cancelled,
            'revenue': float(revenue),
            'watercraft': watercraft_total,
            'watercraft_available': watercraft_available,
            'today_bookings': today_bookings,
        },
        'top_watercraft': top_watercraft,
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def watercraft_availability(request, pk):
    """Return all blocking (pending/approved) reservations for a watercraft on a given date."""
    date_param = request.query_params.get('date')
    if not date_param:
        return Response({'detail': 'date query param required.'}, status=400)
    qs = Reservation.objects.filter(
        watercraft_id=pk,
        reservation_date=date_param,
        status__in=[Reservation.Status.PENDING, Reservation.Status.APPROVED],
    ).values('id', 'start_time', 'end_time', 'status')
    return Response(list(qs))
