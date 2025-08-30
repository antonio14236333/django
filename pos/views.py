from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Category, Product, Sale, SaleItem
from .forms import CheckoutForm, FilterForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .forms import CheckoutForm, FilterForm, CategoryForm, ProductForm


def _get_cart(request):
    return request.session.get("cart", {})  # {product_id: qty}

def _save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True

def add_to_cart(request, product_id):
    if request.method != "POST":
        return redirect("pos:sell")
    product = get_object_or_404(Product, id=product_id, active=True)
    cart = _get_cart(request)
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    _save_cart(request, cart)
    return redirect("pos:sell")

def decrease_from_cart(request, product_id):
    if request.method != "POST":
        return redirect("pos:sell")
    cart = _get_cart(request)
    pid = str(product_id)
    if pid in cart:
        cart[pid] -= 1
        if cart[pid] <= 0:
            cart.pop(pid)
    _save_cart(request, cart)
    return redirect("pos:sell")

def remove_from_cart(request, product_id):
    if request.method != "POST":
        return redirect("pos:sell")
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    _save_cart(request, cart)
    return redirect("pos:sell")

def clear_cart(request):
    if request.method == "POST":
        _save_cart(request, {})
    return redirect("pos:sell")

def _cart_context(request):
    cart = _get_cart(request)
    items = []
    total = Decimal("0.00")
    if cart:
        products = Product.objects.filter(id__in=[int(k) for k in cart.keys()], active=True)
        for p in products:
            qty = int(cart.get(str(p.id), 0))
            line_total = p.price * qty
            items.append({"product": p, "qty": qty, "line_total": line_total})
            total += line_total
    return items, total.quantize(Decimal("0.01"))

def sell_view(request):
    category_id = request.GET.get("cat")
    categories = Category.objects.filter(active=True)
    products = Product.objects.filter(active=True)
    if category_id:
        products = products.filter(category_id=category_id)

    items, total = _cart_context(request)
    return render(request, "pos/sell.html", {
        "categories": categories,
        "products": products,
        "items": items,
        "total": total,
        "checkout_form": CheckoutForm(),
        "selected_cat": int(category_id) if category_id else None
    })

@transaction.atomic
def checkout(request):
    if request.method != "POST":
        return redirect("pos:sell")
    items, total = _cart_context(request)
    if not items:
        messages.error(request, "El carrito está vacío.")
        return redirect("pos:sell")

    form = CheckoutForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Datos de pago inválidos.")
        return redirect("pos:sell")

    method = form.cleaned_data["payment_method"]
    cash_given = form.cleaned_data.get("cash_given")
    change = None

    if method == "cash":
        if cash_given is None:
            messages.error(request, "Ingresa el efectivo recibido.")
            return redirect("pos:sell")
        if cash_given < total:
            messages.error(request, "El efectivo no cubre el total.")
            return redirect("pos:sell")
        change = (cash_given - total).quantize(Decimal("0.01"))

    sale = Sale.objects.create(
        payment_method=method,
        total=total,
        cash_given=cash_given if method == "cash" else None,
        change=change if method == "cash" else None,
    )
    # Guardar items
    for it in items:
        SaleItem.objects.create(
            sale=sale,
            product=it["product"],
            quantity=it["qty"],
            price=it["product"].price,
        )
        # opcional: bajar stock simple
        if it["product"].stock > 0:
            it["product"].stock = max(0, it["product"].stock - it["qty"])
            it["product"].save(update_fields=["stock"])

    # Limpiar carrito
    request.session["cart"] = {}
    request.session.modified = True

    if method == "card":
        messages.success(request, f"Venta #{sale.id} registrada. Cobra con Clip 💳.")
    else:
        messages.success(request, f"Venta #{sale.id} registrada. Cambio: ${change} 💵.")
    return redirect("pos:sell")

def history_view(request):
    form = FilterForm(request.GET or None)
    qs = Sale.objects.all()
    method = "all"
    month = year = None

    if form.is_valid():
        method = form.cleaned_data.get("method") or "all"
        month = form.cleaned_data.get("month")
        year = form.cleaned_data.get("year")

    if method in ("cash","card"):
        qs = qs.filter(payment_method=method)
    if year:
        qs = qs.filter(created_at__year=year)
    if month:
        qs = qs.filter(created_at__month=month)

    total_sum = sum(s.total for s in qs)
    return render(request, "pos/history.html", {
        "form": form,
        "sales": qs.select_related().order_by("-created_at")[:500],
        "total_sum": total_sum,
        "sel_method": method, "sel_month": month, "sel_year": year
    })
def _is_staff(user):  # helper
    return user.is_authenticated and user.is_staff

@user_passes_test(_is_staff)
def manage_categories(request):
    from .models import Category
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría creada/actualizada.")
            return redirect("pos:manage_categories")
    else:
        form = CategoryForm()
    categories = Category.objects.all().order_by("name")
    return render(request, "pos/manage_categories.html", {"form": form, "categories": categories})

@user_passes_test(_is_staff)
def delete_category(request, pk):
    from .models import Category
    c = get_object_or_404(Category, pk=pk)
    try:
        c.delete()  # on_delete PROTECT en Product impedirá borrar si tiene productos
        messages.success(request, "Categoría eliminada.")
    except Exception as e:
        messages.error(request, f"No se puede eliminar: {e}")
    return redirect("pos:manage_categories")

@user_passes_test(_is_staff)
def manage_products(request):
    from .models import Product
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado/actualizado.")
            return redirect("pos:manage_products")
    else:
        form = ProductForm()
    products = Product.objects.select_related("category").all().order_by("name")
    return render(request, "pos/manage_products.html", {"form": form, "products": products})

@user_passes_test(_is_staff)
def delete_product(request, pk):
    from .models import Product
    p = get_object_or_404(Product, pk=pk)
    p.delete()
    messages.success(request, "Producto eliminado.")
    return redirect("pos:manage_products")