import django.contrib.auth.models
from rest_framework import viewsets, permissions, generics, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import ModelFilter
from .models import RetailObject, Product, UserToRetailObject
from .serializers import RetailObjectSerializer, ProductSerializer, GenerateQrRequestSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .tasks import send_email_with_qr


class RetailObjectViewSet(viewsets.ModelViewSet):
    queryset = RetailObject.objects.all()
    renderer_classes = [JSONRenderer]
    serializer_class = RetailObjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ModelFilter
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.username in django.contrib.auth.models.User.objects.filter(
                is_superuser=True).values_list('username', flat=True):
            return RetailObject.objects.select_related()
        else:
            return RetailObject.objects.filter(retail_name=UserToRetailObject.objects.filter(
                user__username=self.request.user.username).values_list('retail_object__retail_name', flat=True).first())


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    renderer_classes = [JSONRenderer]
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class SendQrCodeAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GenerateQrRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        retail_object_id = serializer.validated_data['retail_object_id']
        recipient_email = serializer.validated_data['email']
        try:
            retail_object = RetailObject.objects.get(id=retail_object_id)
            send_email_with_qr.delay(retail_object.id, recipient_email)  # Асинхронная задача
            return Response({'message': 'QR-код был успешно отправлен на ваш email.'}, status=status.HTTP_200_OK)
        except RetailObject.DoesNotExist:
            return Response({'error': 'Объект сети не найден.'}, status=status.HTTP_404_NOT_FOUND)

