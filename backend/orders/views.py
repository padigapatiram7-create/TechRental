from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from cart.models import Cart
from .models import Order, OrderRow
from .serializers import OrderSerializer


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        address = data.get('address') or {}
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'detail': 'Your cart is empty.'}, status=400)
        required = ('full_name', 'phone', 'address', 'city', 'state', 'pincode')
        if any(not address.get(field) for field in required):
            raise ValidationError('Address fields are required.')
        if data.get('payment_method') not in ('COD', 'CARD'):
            raise ValidationError({'payment_method': 'COD or CARD required.'})
        if data.get('id_proof') not in ('AADHAAR', 'PASSPORT', 'DRIVING LICENCE'):
            raise ValidationError({'id_proof': 'Invalid ID proof.'})
        order = Order.objects.create(
            renter=request.user, payment_method=data['payment_method'], id_proof=data['id_proof'],
            full_name=address['full_name'], phone=address['phone'], address=address['address'],
            city=address['city'], state=address['state'], pincode=address['pincode'])
        for item in cart.items.select_related('gadget'):
            gadget = item.gadget
            OrderRow.objects.create(
                order=order, lender=gadget.lender, gadget=gadget,
                gadget_title=gadget.title, gadget_brand=gadget.brand,
                gadget_deposit=gadget.deposit, gadget_image=gadget.imageUrl,
                gadget_price=gadget.price, quantity=item.quantity)
        cart.items.all().delete()
        return Response(OrderSerializer(order).data, status=201)


class MyOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(renter=request.user).order_by('-created_at')
        return Response(OrderSerializer(orders, many=True).data)


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, renter=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'No such order.'}, status=404)
        return Response(OrderSerializer(order).data)

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, renter=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'No such order.'}, status=404)
        if order.rows.exclude(status='placed').exists():
            return Response({'detail': 'Order can no longer be cancelled.'}, status=400)
        order.rows.update(status='cancelled')
        return Response(OrderSerializer(order).data)

# Create your views here.
