"""
URL mapping for the road app.
"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from road import views

router = DefaultRouter()
router.register('roads', views.RoadViewSet)
router.register('velocity_reads', views.ReadViewSet, basename='read')
router.register('classification', views.ClassificationViewSet)


app_name = 'road'

urlpatterns = [
    path('', include(router.urls))
]
