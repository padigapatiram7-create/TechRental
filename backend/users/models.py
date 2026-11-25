from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(blank=True)
    user_type = models.CharField(
        max_length=10,
        choices=(('renter', 'Renter'), ('lender', 'Lender')),
        default='renter',
    )

# Create your models here.
