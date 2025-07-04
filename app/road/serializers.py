"""
Serializers for Road APIs
"""

from rest_framework import serializers

from core.models import Road

from rest_framework_gis import serializers as gis_serializers
from rest_framework_gis.fields import GeometryField, GeometrySerializerMethodField



class RoadSerializer(serializers.ModelSerializer):
    """ Serializer for road. """

    class Meta:
        model = Road
        fields = ['id','length']
        read_only_fields = ['id']  #  Make sure that users can´t change user id from road


class RoadDetailSerializer(RoadSerializer):
    """ Serializer for road detial view."""

    class Meta(RoadSerializer.Meta):
        fields=RoadSerializer.Meta.fields + ['segment']