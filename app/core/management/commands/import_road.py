import csv
import os
from decimal import Decimal
from core.models import(
    Road,
    Velocity_Reads,
    User,
    Classification
)

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import LineString
from decimal import Decimal


class Command(BaseCommand):
    """Django command to import inicial data."""

    def handle(self, *args, **options):
        """Entry point for command."""
        if not Road.objects.exists():
            self.stdout.write("Populating database...")

            with open('Traffic_Speed/traffic_speed.csv', newline='') as dataFile:
                reader = csv.DictReader(dataFile)
                for line in reader:
                    road,_=Road.objects.get_or_create(
                        name = 'Road '+ str(line['ID']),
                        segment = LineString(
                        (float(line['Lat_start']),float(line['Long_start'])),
                        (float(line['Lat_end']),float(line['Lat_end']))
                        ),
                        length = float(line['Length'])
                        
                    )
                    Velocity_Reads.objects.get_or_create(
                        road=road,
                        read_value=Decimal(line['Speed'])
                    )
            
            self.stdout.write(self.style.SUCCESS("Database populated!"))
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write("Creating dev SuperUser...")
            get_user_model().objects.create_superuser(
                email = os.environ.get('DJANGO_ADMIN_USER'),
                password = os.environ.get('DJANGO_ADMIN_PASS')
            )
            self.stdout.write("Dev SuperUser created")
        if not Classification.objects.exists():
            Classification.objects.create(
                min_value = Decimal('20'),
                max_value = Decimal('50')
            )

