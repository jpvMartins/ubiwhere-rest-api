"""
Database models.
"""

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.gis.db import models as gis_models


class UserManager(BaseUserManager):
    """
    Manager for users.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create, save and return a new user.
        """
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Create and return a new superuser.
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    User in the system.
    """

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        """Return string representation of our user."""
        return self.email


class Road(models.Model):
    """
    Road object.
    """
    name = models.CharField(max_length=255)
    segment = gis_models.LineStringField()
    length = models.FloatField()

    class Meta:
        constraints = [ models.UniqueConstraint(
            fields = ['name','segment'],
            name = 'unique_road'
        ),
        ]

    def __str__(self):
        """Return string representation of our Road"""
        return f"Road {self.id} ({self.segment})"


class Velocity_Reads(models.Model):
    """Velocity-Reads object."""
    road = models.ForeignKey(Road,on_delete=models.CASCADE, related_name='velocity_reads')
    read_value=models.DecimalField(max_digits=5, decimal_places=2)
    read_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string visualization of our read."""
        return f"Read {self.read_value} at {self.road}"
    
class Classification(models.Model):
    """
    Classification object.
    """

    min_value = models.DecimalField(max_digits=5, decimal_places=2)
    max_value = models.DecimalField(max_digits=5, decimal_places=2)


    def __str__(self):
        return f"{self.id}: min_value: {self.min_value} , max_value: {self.max_value}"
