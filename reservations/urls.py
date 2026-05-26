from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reservations', views.ReservationViewSet, basename='reservation')

urlpatterns = router.urls + [
    path('admin/reservations', views.admin_reservations, name='admin-reservations'),
    path('admin/reservations/<int:pk>/status', views.admin_update_status, name='admin-update-status'),
    path('admin/stats', views.admin_stats, name='admin-stats'),
    path('watercraft/<int:pk>/availability', views.watercraft_availability, name='watercraft-availability'),
]
