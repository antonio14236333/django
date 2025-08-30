from django.urls import path
from . import views

app_name = "pos"

urlpatterns = [
    path("sell/", views.sell_view, name="sell"),
    path("add/<int:product_id>/", views.add_to_cart, name="add"),
    path("dec/<int:product_id>/", views.decrease_from_cart, name="dec"),
    path("rm/<int:product_id>/", views.remove_from_cart, name="rm"),
    path("clear/", views.clear_cart, name="clear"),
    path("checkout/", views.checkout, name="checkout"),
    path("history/", views.history_view, name="history"),


    path("manage/categories/", views.manage_categories, name="manage_categories"),
    path("manage/categories/<int:pk>/delete/", views.delete_category, name="delete_category"),
    path("manage/products/", views.manage_products, name="manage_products"),
    path("manage/products/<int:pk>/delete/", views.delete_product, name="delete_product"),
]
