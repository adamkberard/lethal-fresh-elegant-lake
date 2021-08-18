# Create your models here.
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings


class PizzaOrder(models.Model):
    # Flavor choices
    FLAVOR_HAWAII = 'Hawaii'
    FLAVOR_REGINA = 'Regina'
    FLAVOR_QUATTRO_FORMAGGI = 'Quattro-Formaggi'
    FLAVOR_CHOICES = (
        (FLAVOR_HAWAII, 'Hawaii'),
        (FLAVOR_REGINA, 'Regina'),
        (FLAVOR_QUATTRO_FORMAGGI, 'Quattro-Formaggi')
    )

    # Size choices
    SIZE_LARGE = "Large"
    SIZE_MEDIUM = "Medium"
    SIZE_CHOICES = (
        (SIZE_LARGE, 'Large'),
        (SIZE_MEDIUM, 'Medium')
    )

    # Crust choices
    CRUST_THIN = "Thin"
    CRUST_CHOICES = [
        (CRUST_THIN, 'Thin')
    ]

    flavor = models.CharField(
        max_length=16,
        choices=FLAVOR_CHOICES,
        default=FLAVOR_HAWAII
    )

    size = models.CharField(
        max_length=6,
        choices=SIZE_CHOICES,
        default=SIZE_MEDIUM
    )

    crust = models.CharField(
        max_length=4,
        choices=CRUST_CHOICES,
        default=CRUST_THIN
    )

    table_number = models.IntegerField(MinValueValidator(30000), blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    ordered_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name="ordered_by")