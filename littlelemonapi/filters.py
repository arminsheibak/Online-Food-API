from django_filters.rest_framework import FilterSet
from .models import MenuItem

class MenuItemFilter(FilterSet):
    class Meta:
        model = MenuItem
        fields = {
            'category_id': ['exact'],
            'price': ['gt', 'lt']
        }