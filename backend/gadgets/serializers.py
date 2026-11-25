from rest_framework import serializers
from .models import Gadget


class GadgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gadget
        fields = '__all__'
        read_only_fields = ('lender', 'rating', 'total_reviews')
