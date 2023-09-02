from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from accounts.models import Account 
from store.models import Product 
from category.models import Category
# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, email=email, password=password)
        
            if user is not None and user.is_active and user.is_superadmin:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials")
        else:
            messages.error(request, "Please provide both email and password")
        
        return redirect('index')
         
    return render(request, 'adminapp/index.html')

def dashboard(request):
    if request.user.is_authenticated:  # Check if the user is logged in
        if request.user.is_superadmin:
            # Superadmin can access the dashboard
            context = {'admin_name': request.user.first_name}  
            return render(request, 'adminapp/dashboard.html', context)
        else:
            
            return HttpResponseForbidden("You don't have permission to access this page.")
    else:
        
        return redirect('login')  

def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('index')

def admin_products(request):
    if request.user.is_superadmin:
        products = Product.objects.select_related('category').all().order_by('id')
        context = {'products': products}
        return render(request, 'adminapp/admin_products.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to access this page.")


def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_images = request.FILES.getlist('product_images')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('quantity')  # Change to 'stock'

        # Rest of your validation and saving code...

        category = Category.objects.get(pk=category_id)

        product = Product(
            product_name=product_name,
            category=category,
            description=description,
            price=price,
            stock=stock,
            is_available=True
        )

        if product_images:
            product.image = product_images[0]

        product.save()
        print(product.product_name)
        return redirect('admin_products')

    categories = Category.objects.all().order_by('id')
    context = {'categories': categories}
    return render(request, 'adminapp/add_product.html', context)

def edit_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return redirect('admin_products')
    
    categories = Category.objects.all().order_by('id')

    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')  # Corrected variable name to match the template
        
        if not (product.product_name and category_id and price and quantity):
            messages.error(request, "Please provide all required fields.")
            return redirect('edit_product', product_id=product_id)

        try:
            price = float(price)
            quantity = int(quantity)
            if price <= 0 or quantity <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Price and quantity must be positive numbers.")
            return redirect('edit_product', product_id=product_id)

        if Product.objects.filter(product_name=product.product_name).exclude(pk=product_id).exists():
            messages.error(request, f"A product with the name '{product.product_name}' already exists.")
            return redirect('edit_product', product_id=product_id)

        category = Category.objects.get(pk=category_id)

        product.category = category
        product.description = description
        product.price = price
        product.stock = quantity  # Corrected the assignment to the 'stock' field
        product.save()

        images = request.FILES.getlist('product_images')
        if images:
            # Clear existing images associated with the product
            product.image = images
            product.save()
            
        return redirect('admin_products')

    context = {
        'product': product,
        'categories': categories,
    }
    return render(request, 'adminapp/edit_product.html', context)

def soft_delete_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return redirect('admin_products')

    # Soft delete the product
    product.soft_deleted = True
    product.is_available = False
    product.save()

    return redirect('admin_products')

def undo_soft_delete_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return redirect('admin_products')

    # Undo the soft delete
    product.soft_deleted = False
    product.is_available = True
    product.save()

    return redirect('admin_products')

def admin_category(request):
    categories = Category.objects.all().order_by('id')  
    context = {'categories': categories}
    return render(request, 'adminapp/admin_category.html', context)

def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_image = request.FILES.get('category_image')

        if not category_name:
            messages.error(request, "Please provide a category name.")
            return redirect('add_category')

        if Category.objects.filter(category_name=category_name).exists():
            messages.error(request, f"A category with the name '{category_name}' already exists.")
            return redirect('add_category')

        category = Category(
            category_name=category_name,
            category_images=category_image
        )
        category.save()

        return redirect('admin_category')

    return render(request, 'adminapp/add_category.html')

def edit_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('admin_category')

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_image = request.FILES.get('category_image')

        if not category_name:
            messages.error(request, "Please provide a category name.")
            return redirect('edit_category', category_id=category_id)

        if Category.objects.filter(category_name=category_name).exclude(pk=category_id).exists():
            messages.error(request, f"A category with the name '{category_name}' already exists.")
            return redirect('edit_category', category_id=category_id)

        category.category_name = category_name
        if category_image:
            category.category_images = category_image
        category.save()

        return redirect('admin_category')

    context = {'category': category}
    return render(request, 'adminapp/edit_category.html', context)

def soft_delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('admin_category')
    category.soft_deleted = True
    category.is_available = False
    category.save()
    return redirect('admin_category')


def undo_soft_delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('admin_category')
    category.soft_deleted = False
    category.is_available = True
    category.save()
    return redirect('admin_category')

def admin_users(request):
    users = Account.objects.all().order_by('id')  
    context = {'users': users}
    return render(request, 'adminapp/admin_users.html', context)

def block_user(request, user_id):
    try:
        user = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return redirect('admin_users')
    user.is_active = False
    user.save()
    return redirect('admin_users')  


def unblock_user(request, user_id):
    try:
        user = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return redirect('admin_users')
    user.is_active = True
    user.save()
    return redirect('admin_users')

def admin_orders(request):
    return render(request, 'adminapp/admin_orders.html')



def admin_coupons(request):
    return render(request, 'adminapp/admin_coupons.html')



def admin_banners(request):
    return render(request, 'adminapp/admin_banners.html')