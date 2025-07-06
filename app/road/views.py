"""
Views for the road APIs.
"""

from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from core.models import (
    Road,
    Velocity_Reads,
    Classification
)
from road import serializers


class RoadViewSet(viewsets.ModelViewSet):
    """View for manage Road APIs.(road/views.py)"""

    serializer_class = serializers.RoadSerializer
    queryset = Road.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Retrive roads ."""
        return self.queryset.order_by('-id')
    


class ReadViewSet(viewsets.ModelViewSet):
    """View for manage Read Apis.(read/)"""

    serializer_class = serializers.ReadSerializer
    queryset = Velocity_Reads.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Retrive roads ."""
        return self.queryset.order_by('-read_at')

class ClassificationViewSet(mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Manage Classification in database"""
    serializer_class = serializers.ClassificationSerializer
    queryset = Classification.objects.filter(id=1)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]




