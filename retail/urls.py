from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.routers import DefaultRouter
from .views import RetailObjectViewSet, ProductViewSet, SendQrCodeAPIView

router = DefaultRouter()
router.register(r'retail', RetailObjectViewSet, basename='retail')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('', include(router.urls)),
    path('api/', SpectacularAPIView.as_view(), name='schema'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('send-qr-code/', SendQrCodeAPIView.as_view(), name='send-qr-code'),
]
