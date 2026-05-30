from rest_framework.routers import DefaultRouter
from .views import WatercraftViewSet

router = DefaultRouter()
router.register(r'watercraft', WatercraftViewSet, basename='watercraft')

urlpatterns = router.urls
