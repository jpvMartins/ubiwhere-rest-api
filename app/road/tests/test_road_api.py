"""
Test  for Road APIs.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.gis.geos import LineString

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Road,
    Velocity_Reads,
    Classification,
)

from road.serializers import (
    RoadSerializer,
    RoadSerializer
)

ROADS_URL = reverse('road:road-list')

def create_user(email='user@examplee.com',password='test123'):
    """Create and return a user with given parameters."""
    return get_user_model().objects.create_user(email=email,password=password)

def create_road(**params):
    """ Create and return a road with given parameters"""

    defaults = {
        'name':'Road name',
        'segment': LineString(
            (104.9460064, 30.75066046),
            (103.9564943, 30.7450801),
        ),
        'length': 1179.2,
    }
    defaults.update(params)

    return Road.objects.create(**defaults)

def road_url(road_id):
    return reverse('road:road-detail',args=[road_id])

    

class PublicRoadApiTests(TestCase):
    """
    Test unauthenticated road API access.
    """

    def setUp(self):
        self.client=APIClient()
        Classification.objects.create(min_value=25,max_value=50)

    def test_retrive_road(self):
        """
        Test retrieving a list of roads.
        """
        create_road()
        create_road(
            name='New Road_name',
            segment = LineString(
                (120.9460064, 35.75066046),
                (120.9564943, 35.7450801),
            ),
        )

        res = self.client.get(ROADS_URL)
        road = Road.objects.all().order_by('-id')
        serializer = RoadSerializer(road, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_detail_road(self):
        """
        Test retrieving a detail of roads.
        """

        road = create_road()
        Velocity_Reads.objects.create(
            road=road,
            read_value = Decimal('15.05'),
        )
        url = road_url(road.id)

        res = self.client.get(url)
        serializer=RoadSerializer(road)
        self.assertEqual(res.data,serializer.data)


        
    def test_update_road_notAlow(self):
        """Test road update error for unauthenticated user."""

        road = create_road()
        payload = {
            'name':'New Road_name',
            'segment': LineString(
                (123.9460064, 35.75066046),
                (123.9564943, 35.7450801),
            ),
            'length': 11.0,
        }
        url = road_url(road.id)
        res = self.client.put(url,payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        road.refresh_from_db()
        for k,v in payload.items():
            self.assertNotEqual(getattr(road,k),v)

    def test_partial_update_road_notAlow(self):
        """Test road partial update error for unauthenticated user."""

        length=12.0
        road = create_road(length=length)
        payload = {
            'length': 11.0,
        }
        url = road_url(road.id)
        res = self.client.patch(url,payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_delete_road_notAlow(self):
        """Tsst delete  error for unauthenticated user."""

        road = create_road()
        url = road_url(road.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Road.objects.filter(id=road.id).exists())



class PrivateRoadApiTests(TestCase):
    """
    Test authenticated road API access.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com',password='testpass123')
        self.client.force_authenticate(self.user)
        Classification.objects.create(min_value=25,max_value=50) # test db doesn´t have classification row


    def test_create_road(self):
        """Test create a road."""
        payload = {
            'name':'Create Road_name',
            'segment': {
                "type": "LineString",
                "coordinates": [
                [113.9460064, 35.75066046],
                [113.9564943, 35.7450801],
                ],
            },
            'length': 11.0,
        }
        res = self.client.post(ROADS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        road = Road.objects.get(id=res.data['id'])
        self.assertAlmostEqual(road.length, payload['length'], places=2)
        self.assertEqual(road.name, payload['name'])
        self.assertEqual(
            [list(c) for c in road.segment.coords],
            payload['segment']['coordinates']
        )

    def test_retrieve_road(self):
        """
        Test retrieving a list of roads.
        """
        create_road()
        create_road(
            name='New Road_name',
            segment = LineString(
                (120.9460064, 35.75066046),
                (120.9564943, 35.7450801),
            ),
        )


        res = self.client.get(ROADS_URL)

        road = Road.objects.all().order_by('-id')
        serializer = RoadSerializer(road, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_update_road(self):
        """Test full update of a road."""


        road = create_road()
        payload = {
            'name':'Road_name',
            'segment': {
                "type": "LineString",
                "coordinates": [
                    [123.9460064, 35.75066046],
                    [123.9564943, 35.7450801],
                ],
            },
            'length': 11.0,
        }
        url = road_url(road.id)
        res = self.client.put(url,payload,format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        road.refresh_from_db()
        self.assertAlmostEqual(road.length, payload['length'], places=2)
        self.assertEqual(road.name, payload['name'])
        self.assertEqual(
            [list(c) for c in road.segment.coords],
            payload['segment']['coordinates']
        )
    def test_partial_update_road(self):
        """Test partial update of a road."""

        length=1179.2
        road = create_road()
        payload = {
            'segment': {
                "type": "LineString",
                "coordinates": [
                    [123.9460064, 35.75066046],
                    [123.9564943, 35.7450801],
                ],
            },
        }
        url = road_url(road.id)
        res = self.client.patch(url,payload,format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        road.refresh_from_db()
        self.assertAlmostEqual(road.length, length, places=2)
        self.assertEqual(road.name, 'Road name')
        self.assertEqual(
            [list(c) for c in road.segment.coords],
            payload['segment']['coordinates']
        )


    def test_delete_road(self):
        """Tsst delete  a list of road."""

        road = create_road()
        url = road_url(road.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Road.objects.filter(id=road.id).exists())

