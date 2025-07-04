"""
Views for the user API.
"""
from rest_framework import generics,authentication,permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the sytem."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for the user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES  # Ensure the renderer classes are set correctly


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]  #  Know if the user is who he says he is
    permission_classes = [permissions.IsAuthenticated] #  Ensure the user is authenticated and which permissions he has

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user  # Return the current authenticated user