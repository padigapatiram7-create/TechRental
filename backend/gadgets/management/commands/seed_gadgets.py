from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from gadgets.models import Gadget
from orders.models import Order, OrderRow
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed TechRentals demo accounts, gadgets, and optional orders'

    def add_arguments(self, parser):
        parser.add_argument('--with-orders', action='store_true')

    def handle(self, *args, **options):
        User = get_user_model()
        lender, _ = User.objects.get_or_create(username='Priya', defaults={'email': 'priya@example.com', 'user_type': 'lender'})
        lender.user_type = 'lender'
        lender.set_password('secret123')
        lender.save()
        renter, _ = User.objects.get_or_create(username='Arjun', defaults={'email': 'arjun@example.com', 'user_type': 'renter'})
        renter.user_type = 'renter'
        renter.set_password('secret123')
        renter.save()

        counts = {'Cameras': 15, 'Consoles': 14, 'Laptops': 13, 'Drones': 12, 'Projectors': 0}
        brands = {'Cameras': 'Sony', 'Consoles': 'Sony', 'Laptops': 'Dell', 'Drones': 'DJI', 'Projectors': 'Epson'}
        gadget_index = 1
        gadget_by_index = {}
        premium_ids = {9, 11, 18, 20, 42, 50}
        if Gadget.objects.count() == 0:
            for category, count in counts.items():
                for number in range(1, count + 1):
                    gadget = Gadget.objects.create(
                        title=f'{brands[category]} {category[:-1]} Kit {number}',
                        brand=brands[category],
                        deposit=5000 + (gadget_index % 7) * 1000,
                        in_the_box='Charging cable, case, one spare battery',
                        category=category,
                        price=299 + gadget_index * 25,
                        imageUrl=f'https://picsum.photos/seed/rental{gadget_index}/600/400',
                        rating=round(3.8 + (gadget_index % 12) / 10, 1),
                        total_reviews=10 + gadget_index,
                        availability='Available',
                        is_premium=gadget_index in premium_ids,
                        description=f'Reliable {category.lower()} kit for professional rental use.',
                        lender=lender,
                    )
                    gadget_by_index[gadget_index] = gadget
                    gadget_index += 1
        else:
            gadget_by_index = {g.id: g for g in Gadget.objects.all()}

        if options['with_orders']:
            if not Order.objects.filter(renter=renter).exists():
                gadgets = list(Gadget.objects.exclude(is_premium=True)[:6])
                for i in range(6):
                    order = Order.objects.create(
                        renter=renter, payment_method='COD', id_proof='PASSPORT',
                        full_name='Arjun Kumar', phone='9876543210', address='12 Park Street',
                        city='Hyderabad', state='Telangana', pincode='500001',
                        created_at=timezone.now() - timedelta(days=i))
                    gadget = gadgets[i]
                    OrderRow.objects.create(
                        order=order, lender=lender, gadget=gadget,
                        gadget_title=gadget.title, gadget_brand=gadget.brand,
                        gadget_deposit=gadget.deposit, gadget_image=gadget.imageUrl,
                        gadget_price=gadget.price, quantity=i + 1,
                        status='delivered')
                    Order.objects.filter(pk=order.pk).update(
                        created_at=timezone.now() - timedelta(days=i))
        self.stdout.write(self.style.SUCCESS('Seed data ready: 54 gadgets, 2 accounts'))
