from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=9999)  # simple

    class Meta:
        ordering = ["name"]
        unique_together = ("category", "name")

    def __str__(self):
        return f"{self.name} (${self.price})"

class Sale(models.Model):
    PAYMENT_CHOICES = [
        ("cash", "Efectivo"),
        ("card", "Tarjeta"),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    cash_given = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    change = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Venta #{self.id} - {self.get_payment_method_display()} - ${self.total}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # precio al momento

    def line_total(self):
        return self.price * self.quantity
