import django_filters
from .models import Product

class ProductsFilter(django_filters.FilterSet):
    # field_name take variable's name (name in this example)
    # creates a query parameter
    # iexact incase-sensitive.  exact case sensitive
    # fields and vars like name => don't add defaulty query params but make them available ony fields and vars
    # fields' lookup_expr default is exact
    name = django_filters.CharFilter(lookup_expr='iexact')
    x = django_filters.CharFilter(field_name= 'description',lookup_expr='icontains')
    price_min = django_filters.NumberFilter(field_name='price' or 8000.00, lookup_expr='gte')

    class Meta:
        model = Product
        fields = ['brand', 'category', 'x', 'price_min']