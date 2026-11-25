from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, DestroyAPIView
from gadgets.models import Gadget
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


def get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(CartSerializer(get_cart(request.user)).data)


class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        gadget_id = request.data.get('gadget')
        quantity = int(request.data.get('quantity', 1))
        if quantity < 1:
            quantity = 1
        try:
            gadget = Gadget.objects.get(id=gadget_id)
        except Gadget.DoesNotExist:
            return Response({'detail': 'No such gadget.'}, status=404)
        if gadget.is_premium and not request.user.is_authenticated:
            return Response({'detail': 'Login required.'}, status=401)
        cart = get_cart(request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, gadget=gadget)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        return Response(CartSerializer(cart).data)


class CartItemUpdateView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def patch(self, request, *args, **kwargs):
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({'quantity': 'This field is required.'}, status=400)
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response({'quantity': 'Enter a valid quantity.'}, status=400)
        if quantity < 1:
            return Response({'quantity': 'Quantity must be at least 1.'}, status=400)
        item = self.get_queryset().filter(pk=kwargs['pk']).first()
        if not item:
            return Response({'detail': 'No such cart item.'}, status=404)
        item.quantity = quantity
        item.save()
        return Response(CartItemSerializer(item).data)

    def delete(self, request, pk):
        item = self.get_queryset().filter(pk=pk).first()
        if not item:
            return Response({'detail': 'No such cart item.'}, status=404)
        item.delete()
        return Response(status=204)


class CartItemDeleteView(DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

# Create your views here.
