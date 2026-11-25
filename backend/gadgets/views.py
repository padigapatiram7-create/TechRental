from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from django_filters.rest_framework import FilterSet
from django_filters import CharFilter, NumberFilter
from .models import Gadget
from .serializers import GadgetSerializer


class GadgetFilter(FilterSet):
    category = CharFilter(field_name='category', lookup_expr='exact')
    brand = CharFilter(field_name='brand', lookup_expr='exact')
    rating = NumberFilter(field_name='rating', lookup_expr='gte')
    is_premium = CharFilter(method='filter_premium')

    class Meta:
        model = Gadget
        fields = ('category', 'brand', 'rating', 'is_premium')

    def filter_premium(self, queryset, name, value):
        if value.lower() == 'true':
            if not self.request.user.is_authenticated:
                raise PermissionDenied('Premium gadgets require login.')
            return queryset.filter(is_premium=True)
        return queryset


class GadgetViewSet(viewsets.ModelViewSet):
    serializer_class = GadgetSerializer
    filterset_class = GadgetFilter
    search_fields = ('title', 'brand')
    ordering_fields = ('price', 'rating')

    def get_queryset(self):
        queryset = Gadget.objects.all().order_by('id')
        premium = self.request.query_params.get('is_premium', '').lower()
        if premium == 'true':
            if not self.request.user.is_authenticated:
                raise NotAuthenticated('Premium gadgets require login.')
            queryset = queryset.filter(is_premium=True)
        elif self.action == 'retrieve':
            gadget_id = self.kwargs.get('pk')
            gadget = Gadget.objects.filter(pk=gadget_id).first()
            if gadget and gadget.is_premium and not self.request.user.is_authenticated:
                raise NotAuthenticated('Premium gadgets require login.')
        elif not self.request.user.is_authenticated:
            queryset = queryset.exclude(is_premium=True)
        return queryset

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        if self.request.user.user_type != 'lender':
            raise PermissionDenied('Only lenders can add gadgets.')
        serializer.save(lender=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.lender_id != self.request.user.id:
            raise PermissionDenied('You can only edit your own gadgets.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.lender_id != self.request.user.id:
            raise PermissionDenied('You can only delete your own gadgets.')
        instance.delete()

# Create your views here.
