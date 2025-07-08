"""
Views for the road APIs.
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from datetime import (
    timedelta
)
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_api_key.permissions import HasAPIKey

from core.models import (
    Car,
    Sensor,
    Plates_Reads
)
from sensor import serializers




class SensorViewSet(viewsets.ModelViewSet):
    """View for manage Road APIs.(road/views.py)"""

    serializer_class = serializers.SensorSerializer
    queryset = Sensor.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    

    def get_queryset(self):
        """Retrive roads ."""
        return self.queryset.order_by('-id')
    


class PlateReadViewSet(viewsets.ModelViewSet):
    """View for manage PlatesRead Apis."""

    serializer_class = serializers.PLatesReadSerializer
    queryset = Plates_Reads.objects.all()
    permission_classes = [HasAPIKey |IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Retrive roads ."""
        return self.queryset.order_by('-read_at')
    
    def create(self, request):
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        if is_many:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    

class CarViewSet(viewsets.ModelViewSet):
    """View for manage Car Apis."""

    serializer_class = serializers.CarSerializer
    queryset = Car.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='license_plate',
                description='License plate to filter reads from the last 24h',
                required=True,
                type=str,
                location=OpenApiParameter.QUERY
            )
        ]
    )
    @action(methods=['get'], detail=False, url_path='pass-by')
    def get_by_plate(self, request):
        """Custom endpoint to filter by license_plate and last 24h."""
        license_plate = request.query_params.get('license_plate')
        if not license_plate:
            return Response(
                {"detail": "Missing license_plate parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            car = Car.objects.get(license_plate=license_plate)
        except Car.DoesNotExist:
            return Response(
                {"error": "Car not recognized."},
                status=status.HTTP_400_BAD_REQUEST
            )

        since = timezone.now() - timedelta(hours=24)
        reads = Plates_Reads.objects.filter(
            car_plate=car,
            read_at__gte=since
        ).select_related('sensor', 'road_segment')

        serializer = serializers.PLatesReadSerializer(reads, many=True)
        return Response(serializer.data)
