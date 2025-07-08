"""
URL mapping for the sensor app.
"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from sensor import views

router = DefaultRouter()
router.register('sensors', views.SensorViewSet)
router.register('plates-read', views.PlateReadViewSet)
router.register('car', views.CarViewSet)


app_name = 'sensor'

urlpatterns = [
    path('', include(router.urls))
]
