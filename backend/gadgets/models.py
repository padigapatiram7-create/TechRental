from django.conf import settings
from django.db import models


class Gadget(models.Model):
    CATEGORIES = (
        ('Cameras', 'Cameras'), ('Consoles', 'Consoles'),
        ('Laptops', 'Laptops'), ('Drones', 'Drones'), ('Projectors', 'Projectors'),
    )
    title = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)
    in_the_box = models.CharField(max_length=300)
    category = models.CharField(max_length=30, choices=CATEGORIES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    imageUrl = models.URLField(blank=True)
    rating = models.FloatField(default=4.0)
    total_reviews = models.PositiveIntegerField(default=0)
    availability = models.CharField(max_length=20, default='Available')
    is_premium = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    lender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gadgets')

    def __str__(self):
        return self.title

# Create your models here.
