"""
Serializers for Road APIs
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field



from core.models import (
    Road,
    Sensor,
    Car,
    Plates_Reads
)



class SensorSerializer(serializers.ModelSerializer):
    """ Serializer for sensor. """

    class Meta:
        model = Sensor
        fields = ['id','name','uuid']
        read_only_fields = ['id','name','uuid']

    
class CarSerializer(serializers.ModelSerializer):
    """Serializer for Car."""

    class Meta:
        model = Car
        fields=['id','license_plate','created_at']


class PLatesReadSerializer(serializers.ModelSerializer):
    """Serializer for plates read view."""
    """Add field to validated_data"""
    # Campos de escrita
    sensor__uuid = serializers.UUIDField(write_only=True)
    car__license_plate = serializers.CharField(write_only=True)
    timestamp = serializers.DateTimeField(source='read_at')

    # Campos de leitura
    sensor = serializers.SerializerMethodField(read_only=True)
    car = serializers.SerializerMethodField(read_only=True)
    road_segment = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Plates_Reads
        fields = [
            'id',
            'road_segment',
            'car__license_plate',
            'car',
            'sensor__uuid',
            'sensor',
            'timestamp',
        ]
        read_only_fields = ['id', 'car', 'sensor']

    @extend_schema_field(serializers.DictField())
    def get_sensor(self, obj):
        return {
            "id": obj.sensor.id,
            "uuid": str(obj.sensor.uuid),
            "name": obj.sensor.name,
        }

    @extend_schema_field(serializers.DictField())
    def get_car(self, obj):
        return {
            "id": obj.car_plate.id,
            "license_plate": obj.car_plate.license_plate,
        }

    def create(self,validated_data):
        """Create a Plate Read"""
        licence = validated_data.pop('car__license_plate')
        sensor_uuid = validated_data.pop('sensor__uuid')
        car_plate,_ = Car.objects.get_or_create(license_plate=licence)
        try:
            sensor = Sensor.objects.get(uuid=sensor_uuid)
        except Sensor.DoesNotExist:
            raise serializers.ValidationError("Sensor not recognized")
        
        return Plates_Reads.objects.create(
            sensor = sensor,
            car_plate=car_plate,
            **validated_data
        )