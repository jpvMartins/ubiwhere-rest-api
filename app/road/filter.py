"""Filter for roads by intensity"""

from django_filters import rest_framework as filters
from core.models import Road, Classification

class RoadFilter(filters.FilterSet):
    intensity = filters.CharFilter(method='filter_by_intensity')

    class Meta:
        model = Road
        fields = {'intensity': ['lt', 'gt'],}

    def filter_by_intensity(self, queryset, name, value):
        thresholds = Classification.objects.first()
        if not thresholds:
            return queryset.none()

        filtered = []
        for road in queryset:
            last_read = road.velocity_reads.order_by('-read_at').first()
            if not last_read:
                continue

            speed = last_read.read_value
            if value == 'baixa' and speed < thresholds.min_value:
                filtered.append(road.id)
            elif value == 'media' and thresholds.min_value <= speed < thresholds.max_value:
                filtered.append(road.id)
            elif value == 'alta' and speed >= thresholds.max_value:
                filtered.append(road.id)

        return queryset.filter(id__in=filtered)
