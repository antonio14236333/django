import json
from decimal import Decimal
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpRequest, HttpResponse

from .forms import CategoryForm, ProductForm
from .prisma_service import prisma_client
from prisma.enums import PaymentType

# Category CRUD
async def category_list(request: HttpRequest) -> HttpResponse:
    async with prisma_client() as prisma:
        categories = await prisma.category.find_many()
    return render(request, 'pos/category_list.html', {'categories': categories})

async def category_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            async with prisma_client() as prisma:
                await prisma.category.create(data=form.cleaned_data)
            return redirect('pos:category_list')
    else:
        form = CategoryForm()
    return render(request, 'pos/category_form.html', {'form': form})

async def category_update(request: HttpRequest, category_id: int) -> HttpResponse:
    async with prisma_client() as prisma:
        category = await prisma.category.find_unique(where={'id': int(category_id)})
        if request.method == 'POST':
            form = CategoryForm(request.POST)
            if form.is_valid():
                await prisma.category.update(
                    where={'id': category.id},
                    data=form.cleaned_data,
                )
                return redirect('pos:category_list')
        else:
            form = CategoryForm(initial={'name': category.name, 'active': category.active})
    return render(request, 'pos/category_form.html', {'form': form, 'category': category})

async def category_delete(request: HttpRequest, category_id: int) -> HttpResponse:
    async with prisma_client() as prisma:
        await prisma.category.delete(where={'id': int(category_id)})
    return redirect('pos:category_list')

# Product CRUD
async def product_list(request: HttpRequest) -> HttpResponse:
    async with prisma_client() as prisma:
        products = await prisma.product.find_many(include={'category': True})
    return render(request, 'pos/product_list.html', {'products': products})

async def product_create(request: HttpRequest) -> HttpResponse:
    async with prisma_client() as prisma:
        categories = await prisma.category.find_many(where={'active': True})
        if request.method == 'POST':
            form = ProductForm(request.POST, categories=categories)
            if form.is_valid():
                data = {
                    'name': form.cleaned_data['name'],
                    'price': float(form.cleaned_data['price']),
                    'active': form.cleaned_data['active'],
                    'category': {'connect': {'id': int(form.cleaned_data['category_id'])}},
                }
                await prisma.product.create(data=data)
                return redirect('pos:product_list')
        else:
            form = ProductForm(categories=categories)
    return render(request, 'pos/product_form.html', {'form': form})

async def product_update(request: HttpRequest, product_id: int) -> HttpResponse:
    async with prisma_client() as prisma:
        product = await prisma.product.find_unique(where={'id': int(product_id)})
        categories = await prisma.category.find_many(where={'active': True})
        if request.method == 'POST':
            form = ProductForm(request.POST, categories=categories)
            if form.is_valid():
                data = {
                    'name': form.cleaned_data['name'],
                    'price': float(form.cleaned_data['price']),
                    'active': form.cleaned_data['active'],
                    'category': {'connect': {'id': int(form.cleaned_data['category_id'])}},
                }
                await prisma.product.update(where={'id': product.id}, data=data)
                return redirect('pos:product_list')
        else:
            form = ProductForm(
                initial={
                    'name': product.name,
                    'price': product.price,
                    'active': product.active,
                    'category_id': product.category_id,
                },
                categories=categories,
            )
    return render(request, 'pos/product_form.html', {'form': form, 'product': product})

async def product_delete(request: HttpRequest, product_id: int) -> HttpResponse:
    async with prisma_client() as prisma:
        await prisma.product.delete(where={'id': int(product_id)})
    return redirect('pos:product_list')

# Sale view
async def sell(request: HttpRequest) -> HttpResponse:
    async with prisma_client() as prisma:
        categories = await prisma.category.find_many(
            where={'active': True},
            include={'products': {'where': {'active': True}}}
        )
        if request.method == 'POST':
            cart = json.loads(request.POST.get('cart', '[]'))
            payment_type = request.POST.get('payment_type')
            cash_received = request.POST.get('cash_received')
            sale = await prisma.sale.create(
                data={
                    'payment_type': payment_type,
                    'cash_received': float(cash_received) if cash_received else None,
                    'items': {
                        'create': [
                            {
                                'product': {'connect': {'id': int(item['id'])}},
                                'quantity': int(item['qty']),
                                'price': float(item['price']),
                            } for item in cart
                        ]
                    }
                }
            )
            return redirect('pos:sell')
    return render(request, 'pos/sell.html', {'categories': categories, 'PaymentType': PaymentType})

# Sales history
async def history(request: HttpRequest) -> HttpResponse:
    payment_type = request.GET.get('payment_type')
    month = request.GET.get('month')
    year = request.GET.get('year')

    where = {}
    if payment_type:
        where['payment_type'] = payment_type
    if year:
        if month:
            start = datetime(int(year), int(month), 1)
            if int(month) == 12:
                end = datetime(int(year) + 1, 1, 1)
            else:
                end = datetime(int(year), int(month) + 1, 1)
        else:
            start = datetime(int(year), 1, 1)
            end = datetime(int(year) + 1, 1, 1)
        where['created_at'] = {'gte': start, 'lt': end}

    async with prisma_client() as prisma:
        sales = await prisma.sale.find_many(where=where, include={'items': True})
    sales_with_total = []
    for sale in sales:
        sale_total = sum(item.quantity * item.price for item in sale.items)
        sales_with_total.append({'sale': sale, 'total': sale_total})
    total = sum(s['total'] for s in sales_with_total)
    return render(
        request,
        'pos/history.html',
        {
            'sales': sales_with_total,
            'total': total,
            'PaymentType': PaymentType,
            'filters': {'payment_type': payment_type, 'month': month, 'year': year},
        },
    )
