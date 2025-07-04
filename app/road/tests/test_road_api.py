"""
Test  for Road APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.gis.geos import LineString

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Road

from road.serializers import RoadSerializer

ROADS_URL = reverse('road:road-list')

def create_user(email='user@examplee.com',password='test123'):
    """Create and return a user with given parameters."""
    return get_user_model().objects.create_user(email=email,password=password)

def create_road(**params):
    """ Create and return a road with given parameters"""

    defaults = {
        'segment': LineString(
            (103.9460064, 30.75066046),
            (103.9564943, 30.7450801),
        ),
        'length': 1179.2,
    }
    defaults.update(params)

    return Road.objects.create(**defaults)


class PublicRoadApiTests(TestCase):
    """
    Test unauthenticated road API access.
    """

    def setUp(self):
        self.client=APIClient()



class PrivateRoadApiTests(TestCase):
    """
    Test authenticated recipe API access.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com',password='testpass123')
        self.client.force_authenticate(self.user)


    def test_retrieve_road(self):
        """
        Test retrieving a list of road.
        """
        create_road()
        create_road()

        res = self.client.get(ROADS_URL)

        road = Road.objects.all().order_by('-id')
        serializer = RoadSerializer(road, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)