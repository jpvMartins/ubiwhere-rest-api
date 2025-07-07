"""
Serializers for Road APIs
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from rest_framework_gis import serializers as gis_serializers
from rest_framework_gis.fields import GeometryField, GeometrySerializerMethodField


from core.models import (
    Road,
    Velocity_Reads,
    Classification,
)




def get_intensity(speed, low, high):
    if speed < low:
        return 'baixa'
    elif speed < high:
        return 'media'
    return 'alta'

class ClassificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Classification
        fields = ['min_value','max_value']

class RoadSerializer(gis_serializers.GeoFeatureModelSerializer):
    """ Serializer for road. """
    total_reads= serializers.SerializerMethodField()
    intensity= serializers.SerializerMethodField()

    class Meta:
        model = Road
        geo_field = 'segment'
        fields = ['id','name','length','total_reads','intensity']
        read_only_fields = ['id']  #  Make sure that users can´t change user id from road

    @extend_schema_field(serializers.IntegerField())
    def get_total_reads(self, obj):
        return obj.velocity_reads.count()
    
    @extend_schema_field(serializers.CharField())
    def get_intensity(self,obj):
        thresholds = Classification.objects.first()
        last_read = obj.velocity_reads.order_by('-read_at').first()
        if last_read:
            return get_intensity(last_read.read_value, thresholds.min_value, thresholds.max_value)
        return None
        
    
    

class ReadSerializer(serializers.ModelSerializer):
    """Serializer for read view."""
    road = serializers.PrimaryKeyRelatedField(queryset=Road.objects.all())


    class Meta:
        model = Velocity_Reads
        fields = ['id','road','read_value','read_at']
        read_only_fileds = ['id','read_at']  

