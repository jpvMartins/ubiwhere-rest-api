"""
Test for reads API"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.contrib.gis.geos import LineString
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Road,
    Velocity_Reads,
)

from road.serializers import (
    ReadSerializer,
)

READS_URL = reverse('road:read-list')

def create_user(email='user@examplee.com',password='test123'):
    """Create and return a user with given parameters."""
    return get_user_model().objects.create_user(email=email,password=password)

def detail_url(read_id):
    """Create and Return a read detail URL."""
    return reverse('road:read-detail',args=[read_id])

def create_road(**params):
    """ Create and return a road with given parameters"""

    defaults = {
        'name': 'Road_name',
        'segment': LineString(
            (103.9460064, 30.75066046),
            (103.9564943, 30.7450801),
        ),
        'length': 1179.2,
    }
    defaults.update(params)

    return Road.objects.create(**defaults)

def create_read(road,**params):
    """ Create and return a read with given parameters"""

    defaults = {
        'road':road,
        'read_value': Decimal('20.05')
    }
    defaults.update(params)

    return Velocity_Reads.objects.create(**defaults)

class PublicReadApiTests(TestCase):
    """
    Test unauthenticated read API access.
    """

    def setUp(self):
        self.client=APIClient()

    def test_retrive_read(self):        
        """
        Test retrieving a list of roads.
        """
        road=create_road()
        create_read(road=road)
        create_read(road=road)

        res = self.client.get(READS_URL)

        read = Velocity_Reads.objects.all().order_by('-id')
        serializer = ReadSerializer(read, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

        
    def test_update_read_notAlow(self):
        """TEst retrieve  a list of read."""

        road=create_road()
        read = create_read(road=road)
        payload = {          
            'road':road.id,
            'read_value': Decimal('21.05')
        }
        url = detail_url(read.id)
        res = self.client.put(url,payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        read.refresh_from_db()
        for k,v in payload.items():
            self.assertNotEqual(getattr(read,k),v)


    def test_delete_read_notAlow(self):
        """Test delete  a list of read."""

        road = create_road()
        read = create_read(road=road)
        url = detail_url(read.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Velocity_Reads.objects.filter(id=read.id).exists())



class PrivateReadApiTests(TestCase):
    """
    Test authenticated read API access.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com',password='testpass123')
        self.client.force_authenticate(self.user)


    def test_create_read(self):
        """Test create a read."""
        road = create_road()
        payload = {
            'road':road.id,
            'read_value': Decimal('20.05')
        }
        res = self.client.post(READS_URL, payload, format = 'json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        read = Velocity_Reads.objects.get(id=res.data['id'])
        self.assertEqual(read.read_value, payload['read_value'])
        self.assertEqual(read.road,road)

    def test_retrieve_read(self):
        """
        Test retrieving a list of reads.
        """

        road=create_road()
        create_read(road=road)
        create_read(road=road)

        res = self.client.get(READS_URL)

        read = Velocity_Reads.objects.all().order_by('-id')
        serializer = ReadSerializer(read, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_read(self):
        """Test full update of a read."""


        read = create_read(road=create_road())
        road = create_road(
            name='New Road_name',
            segment = LineString(
                (120.9460064, 35.75066046),
                (120.9564943, 35.7450801),
            ),
        )
        payload = {
            'road':road.id,
            'read_value': Decimal('22.05')
        }
        url = detail_url(read.id)
        res = self.client.put(url,payload,format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        read.refresh_from_db()
        self.assertEqual(read.read_value, payload['read_value'])
        self.assertEqual(read.road,road)

    def test_partial_update_read(self):
        """Test partial update of a read."""

        value=Decimal('22.05')
        road = create_road()
        read = create_read(road=road,read_value=value)
        payload = {
            'road':road.id,
            'read_value': Decimal('20.05')
        }
        url = detail_url(read.id)
        res = self.client.patch(url,payload,format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        read.refresh_from_db()
        self.assertEqual(read.road, road)
        self.assertEqual(read.read_value, payload['read_value'])

    def test_delete_read(self):
        """Tsst delete  a list of read."""

        read = create_read(road=create_road())
        url = detail_url(read.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Velocity_Reads.objects.filter(id=read.id).exists())



    