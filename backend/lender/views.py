from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum
from gadgets.models import Gadget
from gadgets.serializers import GadgetSerializer
from orders.models import OrderRow
from orders.serializers import OrderRowSerializer


def lender_only(user):
    if not user.is_authenticated or user.user_type != 'lender':
        raise PermissionDenied('Lender account required.')


class LenderGadgetsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lender_only(request.user)
        gadgets = Gadget.objects.filter(lender=request.user)
        search = request.query_params.get('search')
        if search:
            gadgets = gadgets.filter(title__icontains=search)
        data = GadgetSerializer(gadgets, many=True).data
        for item, gadget in zip(data, gadgets):
            item['image_url'] = item.pop('imageUrl')
        return Response({'count': gadgets.count(), 'results': data})


class LenderOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lender_only(request.user)
        rows = OrderRow.objects.filter(lender=request.user).select_related('order').order_by('-order__created_at')
        data = []
        for row in rows:
            data.append({
                'id': row.id, 'order': row.order_id, 'gadget': row.gadget_title,
                'quantity': row.quantity, 'amount': f'{row.amount:.2f}', 'status': row.status,
            })
        return Response(data)


class LenderOrderActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        lender_only(request.user)
        try:
            row = OrderRow.objects.get(pk=pk, lender=request.user)
        except OrderRow.DoesNotExist:
            return Response({'detail': 'No such order row.'}, status=404)
        next_status = {'placed': 'shipped', 'shipped': 'delivered'}
        if row.status not in next_status:
            return Response({'detail': 'Status cannot move forward.'}, status=400)
        row.status = next_status[row.status]
        row.save()
        return Response({'id': row.id, 'status': row.status})


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lender_only(request.user)
        rows = OrderRow.objects.filter(lender=request.user)
        today = timezone.now().date()
        chart = []
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            sold = sum(r.amount for r in rows.filter(order__created_at__date=day))
            chart.append({'date': day.isoformat(), 'sales': float(sold)})
        statuses = list(rows.values('status').annotate(count=Count('id')))
        top = list(rows.values('gadget_title').annotate(
            sold=Sum('quantity'), revenue=Sum('gadget_price')).order_by('-sold')[:5])
        return Response({
            'total_sales': f'{sum((r.amount for r in rows), 0):.2f}',
            'total_orders': rows.values('order').distinct().count(),
            'gadgets': Gadget.objects.filter(lender=request.user).count(),
            'still_to_send': rows.filter(status='placed').count(),
            'chart': chart,
            'statuses': statuses,
            'top_gadgets': top,
        })

# Create your views here.
