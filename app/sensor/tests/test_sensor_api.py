"""
Test  for Sensor APIs.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.gis.geos import LineString
import uuid

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Sensor,
    Velocity_Reads,
    Classification,
)

from sensor.serializers import (
    SensorSerializer,
    SensorSerializer
)

SENSOR_URL = reverse('sensor:sensor-list')

def create_user(email='user@examplee.com',password='test123'):
    """Create and return a user with given parameters."""
    return get_user_model().objects.create_user(email=email,password=password)

def create_sensor(**params):
    """ Create and return a sensor with given parameters"""

    defaults = {
        'name':'Sensor name',
        'uuid': uuid.uuid4()
    }
    defaults.update(params)

    return Sensor.objects.create(**defaults)

def sensor_url(sensor_id):
    return reverse('sensor:sensor-detail',args=[sensor_id])

    

class PublicSensorApiTests(TestCase):
    """
    Test unauthenticated sensor API access.
    """

    def setUp(self):
        self.client=APIClient()
        Classification.objects.create(min_value=25,max_value=50)

    def test_retrive_sensor(self):
        """
        Test retrieving a list of sensors.
        """
        create_sensor()
        create_sensor(
            name='New Sensor_name',
            uuid=uuid.uuid4()
        )

        res = self.client.get(SENSOR_URL)
        sensor = Sensor.objects.all().order_by('-id')
        serializer = SensorSerializer(sensor, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_detail_sensor(self):
        """
        Test retrieving a detail of sensors.
        """

        sensor = create_sensor()
        Velocity_Reads.objects.create(
            sensor=sensor,
            read_value = Decimal('15.05'),
        )
        url = sensor_url(sensor.id)

        res = self.client.get(url)
        serializer=SensorSerializer(sensor)
        self.assertEqual(res.data,serializer.data)


        
    def test_update_sensor_notAlow(self):
        """Test sensor update error for unauthenticated user."""

        sensor = create_sensor()
        payload = {
            'name':'New Sensor_name',
            'segment': LineString(
                (123.9460064, 35.75066046),
                (123.9564943, 35.7450801),
            ),
            'length': 11.0,
        }
        url = sensor_url(sensor.id)
        res = self.client.put(url,payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        sensor.refresh_from_db()
        for k,v in payload.items():
            self.assertNotEqual(getattr(sensor,k),v)

    def test_partial_update_sensor_notAlow(self):
        """Test sensor partial update error for unauthenticated user."""

        length=12.0
        sensor = create_sensor(length=length)
        payload = {
            'length': 11.0,
        }
        url = sensor_url(sensor.id)
        res = self.client.patch(url,payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_delete_sensor_notAlow(self):
        """Tsst delete  error for unauthenticated user."""

        sensor = create_sensor()
        url = sensor_url(sensor.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Sensor.objects.filter(id=sensor.id).exists())



class PrivateSensorApiTests(TestCase):
    """
    Test authenticated sensor API access.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com',password='testpass123')
        self.client.force_authenticate(self.user)
        Classification.objects.create(min_value=25,max_value=50) # test db doesn´t have classification row
        self.api_key = '23231c7a-80a7-4810-93b3-98a18ecfbc42'
        self.headers = {'X_API_KEY': self.api_key}


    def test_create_sensor(self):
        """Test create a sensor."""
        payload = {
            'name':'Create Sensor_name',
            'segment': {
                "type": "LineString",
                "coordinates": [
                [113.9460064, 35.75066046],
                [113.9564943, 35.7450801],
                ],
            },
            'length': 11.0,
        }
        res = self.client.post(SENSOR_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        sensor = Sensor.objects.get(id=res.data['id'])
        self.assertAlmostEqual(sensor.length, payload['length'], places=2)
        self.assertEqual(sensor.name, payload['name'])
        self.assertEqual(
            [list(c) for c in sensor.segment.coords],
            payload['segment']['coordinates']
        )

    def test_retrieve_sensor(self):
        """
        Test retrieving a list of sensors.
        """
        create_sensor()
        create_sensor(
            name='New Sensor_name',
            segment = LineString(
                (120.9460064, 35.75066046),
                (120.9564943, 35.7450801),
            ),
        )


        res = self.client.get(SENSOR_URL)

        sensor = Sensor.objects.all().order_by('-id')
        serializer = SensorSerializer(sensor, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_update_sensor(self):
        """Test full update of a sensor."""


        sensor = create_sensor()
        payload = {
            'name':'Sensor_name',
            'segment': {
                "type": "LineString",
                "coordinates": [
                    [123.9460064, 35.75066046],
                    [123.9564943, 35.7450801],
                ],
            },
            'length': 11.0,
        }
        url = sensor_url(sensor.id)
        res = self.client.put(url,payload,format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        sensor.refresh_from_db()
        self.assertAlmostEqual(sensor.length, payload['length'], places=2)
        self.assertEqual(sensor.name, payload['name'])
        self.assertEqual(
            [list(c) for c in sensor.segment.coords],
            payload['segment']['coordinates']
        )
    def test_partial_update_sensor(self):
        """Test partial update of a sensor."""

        length=1179.2
        sensor = create_sensor()
        payload = {
            'segment': {
                "type": "LineString",
                "coordinates": [
                    [123.9460064, 35.75066046],
                    [123.9564943, 35.7450801],
                ],
            },
        }
        url = sensor_url(sensor.id)
        res = self.client.patch(url,payload,format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        sensor.refresh_from_db()
        self.assertAlmostEqual(sensor.length, length, places=2)
        self.assertEqual(sensor.name, 'Sensor name')
        self.assertEqual(
            [list(c) for c in sensor.segment.coords],
            payload['segment']['coordinates']
        )


    def test_delete_sensor(self):
        """Tsst delete  a list of sensor."""

        sensor = create_sensor()
        url = sensor_url(sensor.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Sensor.objects.filter(id=sensor.id).exists())

