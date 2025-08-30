from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_update, name='category_update'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.product_update, name='product_update'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('sell/', views.sell, name='sell'),
    path('history/', views.history, name='history'),
]
