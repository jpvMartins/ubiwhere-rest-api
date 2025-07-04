"""
Serializers for user API view.
"""

from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _
from rest_framework import serializers




class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name' ]  #   Fileds to be included in the request/response (is_staff needs to be define by the admin    )
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}


    """ Override the create and update methods to handle password encryption."""
    def create(self, validated_data):
        """Create a new user with encrypted password and return it."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and returning it."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                _('Must include "email" and "password".'),
                code='authorization',
            )

        user = authenticate(
            request=self.context.get('request'),
            username=email, password=password
        )

        if not user:
            raise serializers.ValidationError(
                _('Unable to authenticate with provided credentials.'),
                code='authorization',
            )

        attrs['user'] = user
        return attrs