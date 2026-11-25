from rest_framework import serializers
from .models import Order, OrderRow


class OrderRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRow
        fields = ('id', 'gadget_title', 'gadget_brand', 'gadget_deposit', 'gadget_image',
                  'gadget_price', 'quantity', 'status', 'lender')
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    rows = OrderRowSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'created_at', 'payment_method', 'id_proof', 'full_name', 'phone',
                  'address', 'city', 'state', 'pincode', 'rows', 'total', 'can_cancel', 'is_paid')

    def get_total(self, obj):
        return f'{sum((row.amount for row in obj.rows.all()), 0):.2f}'

    def get_can_cancel(self, obj):
        return bool(obj.rows.count()) and all(row.status == 'placed' for row in obj.rows.all())

    def get_is_paid(self, obj):
        return obj.payment_method == 'CARD' or obj.is_delivered
