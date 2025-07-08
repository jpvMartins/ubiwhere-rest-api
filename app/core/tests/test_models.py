

"""
Testes for models.
"""
from decimal import Decimal

from django.contrib.gis.geos import LineString
from django.test import TestCase   # base class for tests
from django.contrib.auth import get_user_model

from core import models

# helper function : get the user model
def create_user(email='user@example.com',password='test123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email,password)

class ModelTests(TestCase):
    """
    Test cases for models.
    """

    def test_create_user_with_email_successful(self):
        """
        Test creating a user with email is successful.
        """
        email = "test@exemple.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Test the email for a new user is normalized.
        """
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TESTE3@EXAMPLE.COM', 'TESTE3@example.com'],
            ['test4@example.com', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='sample123'
            )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """
        Test creating user without email raises error.
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """
        Test creating a superuser.
        """
        user = get_user_model().objects.create_superuser(
            'test@exemple.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_road_segment(self):
        """
        Test creating a road segment is successful.
        """
        road = models.Road.objects.create(
            segment=LineString(
                (103.9460064, 30.75066046),
                (103.9564943, 30.7450801)
            ),
            length=1179.207157,
        )

        self.assertEqual(str(road),f"Road {road.id} ({road.segment})")

    def test_created_read(self):
        """
        TesT createing a read sucssesful.
        """
        road = models.Road.objects.create(
            segment=LineString(
                (103.9460064, 30.75066046),
                (103.9564943, 30.7450801)
            ),
            length=1179.207157,
        )

        read = models.Velocity_Reads.objects.create(
            road = road,
            read_value = Decimal('30.05')
        )        
        self.assertEqual(str(read),f"Read {read.read_value} at {read.road}")

    def test_created_sensor(self):
        """
        Test creating a sensor sucssesful.
        """
        sensor = models.Sensor.objects.create(
            name= "Test Sensor",
            uuid= "a3e86bd0-c19f-44e9-84c0-eadf4d4da197"
        )
        self.assertEqual(str(sensor),f" Sensor {sensor.name}: uuid - {sensor.uuid}")