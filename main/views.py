from decimal import Decimal
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .models import Admin, Inquiry, Product


def _get_cart_items(request):
    cart = request.session.get('cart', {})
    product_ids = [int(product_id) for product_id in cart.keys()]
    products = Product.objects.filter(id__in=product_ids)

    items = []
    total = Decimal('0.00')

    for product in products:
        qty = int(cart.get(str(product.id), 0))
        if qty <= 0:
            continue
        line_total = Decimal(str(product.price)) * qty
        total += line_total
        items.append({
            'product': product,
            'quantity': qty,
            'line_total': line_total,
        })

    return items, total


def home(request):
    featured = Product.objects.filter(is_featured=True).order_by('-created_at')[:4]
    if not featured:
        featured = Product.objects.order_by('-created_at')[:4]

    collection_fallbacks = {
        'kuchipudi': 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80',
        'bharatnatyam': 'https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=900&q=80',
        'mohiniyattam': 'https://images.unsplash.com/photo-1508700115892-45d8e1de7d87?auto=format&fit=crop&w=900&q=80',
        'jewellery': 'https://images.unsplash.com/photo-1617038220319-276d3cfab638?auto=format&fit=crop&w=900&q=80',
        'antique_jewellery': 'https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=80',
        'hair_floral': 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80',
    }
    collection_categories = {
        'kuchipudi': 'Kuchipudi',
        'bharatnatyam': 'Bharatnatyam',
        'mohiniyattam': 'Mohiniyattam',
        'jewellery': 'Jewellery',
        'antique_jewellery': 'Antique Jewellery',
        'hair_floral': 'Hair & Floral',
    }
    collection_images = {}
    for key, category in collection_categories.items():
        product = Product.objects.filter(category=category, image__isnull=False).exclude(image='').first()
        collection_images[key] = product.image.url if product else collection_fallbacks[key]

    return render(request, 'index.html', {
        'featured_products': featured,
        'collection_images': collection_images,
    })


def catalog(request):
    products = Product.objects.all().order_by('-created_at')[:6]
    return render(request, 'catalog.html', {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related,
    })


def catalog_filter(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', 'all')
    style = request.GET.get('style', 'all')
    max_price = request.GET.get('max_price', 20000)
    page = int(request.GET.get('page', 1))

    products = Product.objects.all().order_by('-created_at')

    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    if category and category != 'all':
        products = products.filter(category=category)

    if style and style != 'all':
        products = products.filter(style=style)

    try:
        products = products.filter(price__lte=Decimal(str(max_price)))
    except Exception:
        pass

    page_size = 6
    start = (page - 1) * page_size
    end = start + page_size
    page_products = products[start:end]

    html = render_to_string('partials/product_cards.html', {
        'products': page_products,
        'request': request,
    })

    return JsonResponse({
        'html': html,
        'has_more': end < products.count(),
        'page': page,
    })


@require_POST
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    # Grab the exact quantity typed into the product page safely
    try:
        qty = int(request.POST.get('quantity', 1))
    except ValueError:
        qty = 1
        
    if qty < 1:
        qty = 1
    
    cart[product_id_str] = cart.get(product_id_str, 0) + qty
    
    request.session['cart'] = cart
    request.session['cart_count'] = sum(cart.values())
    request.session.modified = True

    return redirect('cart_page')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        
    request.session['cart'] = cart
    request.session['cart_count'] = sum(cart.values())
    request.session.modified = True
    
    return redirect('cart_page')


@require_POST
def toggle_favorite(request, product_id):
    favorites = request.session.get('favorites', [])
    product_id_str = str(product_id)

    if product_id_str in favorites:
        favorites.remove(product_id_str)
        is_favorite = False
    else:
        favorites.append(product_id_str)
        is_favorite = True

    request.session['favorites'] = favorites
    request.session['favorite_count'] = len(favorites)

    return JsonResponse({
        'success': True,
        'favorite_count': len(favorites),
        'is_favorite': is_favorite,
    })


def cart_page(request):
    items, total = _get_cart_items(request)
    return render(request, 'cart.html', {'items': items, 'total': total})


def checkout(request):
    items, total = _get_cart_items(request)

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        
        # Grab the separated address fields
        house_name = request.POST.get('house_name', '').strip()
        street = request.POST.get('street', '').strip()
        city = request.POST.get('city', '').strip()
        pincode = request.POST.get('pincode', '').strip()

        if not customer_name or not phone_number:
            messages.error(request, 'Please add your name and phone number to place the order.')
            return render(request, 'checkout.html', {'items': items, 'total': total})

        # Combine the address fields for the admin dashboard
        delivery_address = f"{house_name}, {street}, {city}, Pincode: {pincode}"
        
        # Add the quantity to the product interest string
        product_names = ', '.join(f"{item['product'].name} (Qty: {item['quantity']})" for item in items)
        
        Inquiry.objects.create(
            customer_name=customer_name,
            phone_number=phone_number,
            product_interest=product_names,
            notes=f"Delivery Address: {delivery_address}",
            status='Pending'
        )

        request.session['cart'] = {}
        request.session['cart_count'] = 0
        return redirect('order_success')

    return render(request, 'checkout.html', {'items': items, 'total': total})


def order_success(request):
    return render(request, 'order_success.html')


def bharatnatyam(request):
    b_products = Product.objects.filter(category='Bharatnatyam')
    return render(request, 'bharatnatyam.html', {'products': b_products})


def mohiniyattam(request):
    m_products = Product.objects.filter(category='Mohiniyattam')
    return render(request, 'mohiniyattam.html', {'products': m_products})


def kuchipudi(request):
    k_products = Product.objects.filter(category='Kuchipudi')
    return render(request, 'kuchipudi.html', {'products': k_products})


def jewellery(request):
    products = Product.objects.filter(category='Jewellery')
    return render(request, 'jewellery.html', {'products': products})


def antique_jewellery(request):
    products = Product.objects.filter(category='Antique Jewellery')
    return render(request, 'antique_jewellery.html', {'products': products})


def hair_floral(request):
    products = Product.objects.filter(category='Hair & Floral')
    return render(request, 'hair_floral.html', {'products': products})


def admin_login(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            admin = Admin.objects.get(Username=username, Password=password)
            request.session['user_id'] = admin.id
            return redirect('a_home')
        except Admin.DoesNotExist:
            messages.error(request, 'Invalid credentials. Please try again.')
            return render(request, 'a_login.html')
    return render(request, 'a_login.html')


def a_home(request):
    if 'user_id' not in request.session:
        return redirect('admin_login')

    total_products = Product.objects.count()
    active_orders = Inquiry.objects.filter(status='Pending').count()
    total_inquiries = Inquiry.objects.count()

    context = {
        'total_products': total_products,
        'active_orders': active_orders,
        'total_inquiries': total_inquiries,
    }
    return render(request, 'a_home.html', context)


def manage_products(request):
    if 'user_id' not in request.session:
        return redirect('admin_login')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            Product.objects.create(
                name=request.POST.get('name'),
                category=request.POST.get('category'),
                style=request.POST.get('style', 'Classic'),
                price=request.POST.get('price'),
                description=request.POST.get('description'),
                sizes=request.POST.get('sizes'),
                image=request.FILES.get('image')
            )

        elif action == 'edit':
            product_id = request.POST.get('product_id')
            prod = Product.objects.get(id=product_id)

            prod.name = request.POST.get('name')
            prod.category = request.POST.get('category')
            prod.style = request.POST.get('style', prod.style)
            prod.price = request.POST.get('price')
            prod.description = request.POST.get('description')
            prod.sizes = request.POST.get('sizes')

            if request.FILES.get('image'):
                prod.image = request.FILES.get('image')

            prod.save()

        elif action == 'delete':
            product_id = request.POST.get('product_id')
            Product.objects.filter(id=product_id).delete()

        return redirect('manage_products')

    all_products = Product.objects.all().order_by('-created_at')
    return render(request, 'manage_products.html', {'products': all_products})


def orders(request):
    if 'user_id' not in request.session:
        return redirect('admin_login')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            Inquiry.objects.create(
                customer_name=request.POST.get('customer_name'),
                phone_number=request.POST.get('phone_number'),
                product_interest=request.POST.get('product_interest'),
                notes=request.POST.get('notes')
            )

        elif action == 'resolve':
            inquiry_id = request.POST.get('inquiry_id')
            Inquiry.objects.filter(id=inquiry_id).update(status='Resolved')

        elif action == 'delete':
            inquiry_id = request.POST.get('inquiry_id')
            Inquiry.objects.filter(id=inquiry_id).delete()

        return redirect('orders')

    all_inquiries = Inquiry.objects.all().order_by('-created_at')
    return render(request, 'orders.html', {'inquiries': all_inquiries})