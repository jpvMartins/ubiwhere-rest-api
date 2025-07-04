"""
Views for the road APIs.
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from core.permissions import IsAdminOrReadOnly

from core.models import Road
from road import serializers


class RoadViewSet(viewsets.ModelViewSet):
    """View for manage Road APIs.(road/views.py)"""

    serializer_class = serializers.RoadDetailSerializer
    queryset = Road.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """Retrive roads ."""
        return self.queryset.order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for the request."""
        if self.action == 'list':
            return serializers.RoadSerializer

        return self.serializer_class

    def perform_create(self,serializer):
        """Create a new road. Give the already authenticated user as user value for foreign key"""
        serializer.save(user=self.request.user)