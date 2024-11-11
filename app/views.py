from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.contrib.auth.forms import UserCreationForm
import pandas as pd
from django.contrib.auth import logout
from .forms import RegistrationForm
from .models import Customer  # Import your Customer model





from .models import Product, Category, Cart, CartItem, Bundle, OrderItem
from .forms import ProductForm
from app.models import Order
def web(request):
    return render(request, 'web.html')


# Home View
def home(request):
    # Fetch all categories for displaying in filters
    categories = Category.objects.all()

    # Start with all products, then filter as needed
    products = Product.objects.all()

    # Check for search and category filters in the request
    query = request.GET.get('q', '')  # Get search term if provided
    category_id = request.GET.get('cat', None)  # Get category ID if provided

    # Filter products by search query if 'q' is provided
    if query:
        products = products.filter(name__icontains=query)

    # Filter products by category if 'cat' is provided
    if category_id:
        products = products.filter(category_id=category_id)

    # Get cart items count if the user is authenticated
    cartItems = 0
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items

    context = {
        'categories': categories,
        'products': products,
        'cartItems': cartItems,
        'query': query,
        'category_id': category_id
    }
    return render(request, 'index.html', context)

def quick_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'index.html', {'product': product})

# Product Views
def product_list(request):
    category_id = request.GET.get('category_id')
    products = Product.objects.all()
    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()
    return render(request, 'your_template.html', {'products': products, 'categories': categories})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Fetch related products or other necessary data if needed
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]  # Fetch 4 related products

    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,  # Pass related products to the template
    })

def search_products(request):
    query = request.GET.get('query', '')
    products = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'shop.html', {'products': products, 'query': query})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form})


def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'confirm_delete.html', {'product': product})

# Category Views
def category_detail(request, category_name):
    products = Product.objects.filter(category__name=category_name)
    return render(request, 'index.html', {'products': products})

def shop_view(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.all()
    if category_slug:
        category = get_object_or_404(Category, name=category_slug)
        products = products.filter(category=category)

    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'shop.html', context)

# Cart and Order Views
# @login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import CartItem, Product  # Make sure CartItem model and Product model are correctly imported
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.total_price for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'cart_total': cart_total})

@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        item.quantity = quantity
        item.save()
    return redirect('cart_view')

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('cart_view')

def cart(request):

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
	else:
		#Create empty cart for now for non-logged in user
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0}

	context = {'items':items, 'order':order}
	return render(request, 'cart.html', context)

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    return render(request, 'checkout.html', {'items': items, 'order': order})

# Bulk Product Addition
def upload_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES['excel_file']
        df = pd.read_excel(excel_file)

        for _, row in df.iterrows():
            Product.objects.create(
                name=row['name'],
                description=row['description'],
                price=row['price'],
                image=row['image'],
                previous_price=row.get('previous_price', 0),
                rating=row.get('rating', 0),
                reviews_count=row.get('reviews_count', 0),
                is_featured=row.get('is_featured', False)
            )
        return redirect('home')
    return render(request, 'upload_excel.html')

# Authentication Views
def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('home')
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user, name=user.username, email=form.cleaned_data.get('email'))
            messages.success(request, f'Account created for {user.username}! You can now log in.')
            return redirect('login')  # Redirect to the login page after registration
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def custom_logout(request):
    logout(request)
    return render(request, 'logout.html')

# Additional Pages
def d1(request):
    return render(request, 'dashboarduser.html')

def about(request):
    return render(request, 'about.html')

def blog(request):
    return render(request, 'blog.html')

def single(request):
    return render(request, 'single.html')

def wishlist(request):
    return render(request, 'wishlist.html')

def shop(request):
    return render(request, 'shop.html')