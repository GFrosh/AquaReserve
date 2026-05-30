from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from .models import Watercraft
from .serializers import WatercraftSerializer
from .permissions import IsAdminOrReadOnly


class WatercraftViewSet(viewsets.ModelViewSet):
    queryset = Watercraft.objects.all()
    serializer_class = WatercraftSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'type', 'location']
    ordering_fields = ['price_per_hour', 'created_at', 'name']
    pagination_class = None  # return full list for the explore page

    def get_queryset(self):
        qs = super().get_queryset()
        wtype = self.request.query_params.get('type')
        available = self.request.query_params.get('available')
        if wtype:
            qs = qs.filter(type=wtype)
        if available is not None:
            qs = qs.filter(is_available=(available.lower() == 'true'))
        return qs
