from django.contrib import admin
from .models import Category, Product, Sale, SaleItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id","name","active")
    search_fields = ("name",)
    list_filter = ("active",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id","name","category","price","active","stock")
    list_filter = ("category","active")
    search_fields = ("name",)

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id","payment_method","total","cash_given","change","created_at")
    list_filter = ("payment_method","created_at")
    inlines = [SaleItemInline]
