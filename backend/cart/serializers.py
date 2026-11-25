from rest_framework import serializers
from decimal import Decimal
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    gadget_title = serializers.CharField(source='gadget.title', read_only=True)
    gadget_deposit = serializers.CharField(source='gadget.deposit', read_only=True)
    gadget_price = serializers.CharField(source='gadget.price', read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'gadget', 'gadget_title', 'gadget_deposit', 'gadget_price', 'quantity')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'total_price')

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_total_price(self, obj):
        total = sum((item.gadget.price * item.quantity for item in obj.items.all()), Decimal('0'))
        return f'{total:.2f}'
