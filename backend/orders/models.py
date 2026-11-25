from django.conf import settings
from django.db import models


class Order(models.Model):
    PAYMENT_CHOICES = (('COD', 'COD'), ('CARD', 'CARD'))
    ID_PROOF_CHOICES = (('AADHAAR', 'Aadhaar'), ('PASSPORT', 'Passport'), ('DRIVING LICENCE', 'Driving Licence'))
    renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    id_proof = models.CharField(max_length=20, choices=ID_PROOF_CHOICES)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return sum((row.amount for row in self.rows.all()), 0)

    @property
    def is_delivered(self):
        return self.rows.exists() and all(row.status == 'delivered' for row in self.rows.all())


class OrderRow(models.Model):
    STATUS_CHOICES = (
        ('placed', 'Placed'), ('shipped', 'Shipped'),
        ('delivered', 'Delivered'), ('cancelled', 'Cancelled'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='rows')
    lender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sold_rows')
    gadget_title = models.CharField(max_length=200)
    gadget_brand = models.CharField(max_length=100)
    gadget_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    gadget_image = models.URLField(blank=True)
    gadget_price = models.DecimalField(max_digits=10, decimal_places=2)
    gadget = models.ForeignKey('gadgets.Gadget', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')

    @property
    def amount(self):
        return self.gadget_price * self.quantity

# Create your models here.
