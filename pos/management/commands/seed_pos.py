from django.core.management.base import BaseCommand
from pos.models import Category, Product

class Command(BaseCommand):
    help = "Crea categorías y productos de ejemplo"

    def handle(self, *args, **kwargs):
        data = {
            "Bebidas": [
                ("Espresso", 35),
                ("Latte", 45),
                ("Matcha Frappe", 65),
                ("Taro Latte", 62),
                ("Cold Brew", 55),
            ],
            "Postres": [
                ("Brownie", 30),
                ("Cheesecake", 48),
                ("Galleta Choco", 25),
            ],
            "Snacks": [
                ("Croissant", 32),
                ("Panini", 68),
            ]
        }
        for cat, prods in data.items():
            c,_ = Category.objects.get_or_create(name=cat, active=True)
            for name, price in prods:
                Product.objects.get_or_create(category=c, name=name, defaults={"price": price, "active": True})
        self.stdout.write(self.style.SUCCESS("Seed listo."))
