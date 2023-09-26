from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import Account 
from orders.models import Order, OrderProduct
from store.models import Product, ProductImage, Variation
from cart.models import Coupon 
from category.models import Category
from django.views.decorators.cache import cache_control, never_cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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

@never_cache
@login_required
def dashboard(request):
    if request.user.is_authenticated:  # Check if the user is logged in
        if request.user.is_superadmin:
            # Superadmin can access the dashboard
            context = {'admin_name': request.user.first_name}  
            return render(request, 'adminapp/dashboard.html', context)
        else:
            
            return redirect('home')
    else:
        
        return redirect('login')  

@never_cache
@login_required
def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('index')

#------------------------------------Product-------------------------------------

@login_required
def admin_products(request):
    if request.user.is_superadmin:
        products = Product.objects.select_related('category').all().order_by('id')
        context = {'products': products}
        return render(request, 'adminapp/admin_products.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to access this page.")

@login_required
def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_images = request.FILES.getlist('product_images')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')

        if not (product_name and category_id ):
            messages.error(request, "Please provide all required fields.")
            return redirect('add_product')


        if Product.objects.filter(product_name=product_name).exists():
            messages.error(request, f"A product with the name '{product_name}' already exists.")
            return redirect('add_product')

        category = Category.objects.get(pk=category_id)

        product = Product(
            product_name=product_name,
            category=category,
            description=description,
            price = price,
            quantity = quantity,
            is_available=True
        )

        if product_images:
            product.image = product_images[0]  

        product.save()  

        # Create ProductImage instances for additional images
        for image in product_images:
            ProductImage.objects.create(product=product, image=image)

        return redirect('admin_products')

    categories = Category.objects.all().order_by('id')
    context = {'categories': categories}
    return render(request, 'adminapp/add_product.html', context)

@login_required
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
        quantity = request.POST.get('quantity')
        
        if not (product.product_name and category_id ):
            messages.error(request, "Please provide all required fields.")
            return redirect('edit_product', product_id=product_id)

        if Product.objects.filter(product_name=product.product_name).exclude(pk=product_id).exists():
            messages.error(request, f"A product with the name '{product.product_name}' already exists.")
            return redirect('edit_product', product_id=product_id)

        category = Category.objects.get(pk=category_id)

        product.category = category
        product.description = description
        product.price = price
        product.quantity = quantity
        product.save()

        images = request.FILES.getlist('product_images')
        if images:
            product.images.all().delete()

            for image in images:
                ProductImage.objects.create(product=product, image=image)
            
        return redirect('admin_products')

    context = {
        'product': product,
        'categories': categories,
    }
    return render(request, 'adminapp/edit_product.html', context)

@login_required
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

@login_required
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
#------------------------------------Varients---------------------------------------------

def admin_varients(request):
    # Retrieve all products along with their related variations
    products = Product.objects.filter(soft_deleted=False)

    context = {
        'products': products,
    }

    return render(request, 'adminapp/admin_varients.html', context)
def add_varients(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        variation_category = request.POST.get('variation_category')
        variation_value = request.POST.get('variation_value')
        

        try:
            product = Product.objects.get(pk=product_id)

            variation = Variation(
                product=product,
                variation_category=variation_category,
                variation_value= variation_value,
            )
            variation.save()

            messages.success(request, "Variants added successfully.")
            return redirect('admin_varients')

        except (Product.DoesNotExist, ValueError):
            messages.error(request, "Invalid input. Please check your data.")
            return redirect('add_varients')

    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'adminapp/add_varients.html', context)

def delete_varient(request, varient_id):
    varient = get_object_or_404(Variation, pk=varient_id)
    if varient.product:
        product = varient.product
        varient.delete()
        messages.success(request, "Variant deleted successfully.")
        return redirect('admin_varients')
    else:
        messages.error(request, "Unable to delete.")
        
    return redirect('admin_varients')
        
#------------------------------------Category---------------------------------------------
@login_required
def admin_category(request):
    categories = Category.objects.all().order_by('id')  
    context = {'categories': categories}
    return render(request, 'adminapp/admin_category.html', context)

@login_required
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

@login_required
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

@login_required
def soft_delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('admin_category')
    category.soft_deleted = True
    category.is_available = False
    category.save()
    return redirect('admin_category')

@login_required
def undo_soft_delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('admin_category')
    category.soft_deleted = False
    category.is_available = True
    category.save()
    return redirect('admin_category')


#-----------------------------------------User-------------------------------------

@login_required
def admin_users(request):
    users = Account.objects.all().order_by('id')  
    context = {'users': users}
    return render(request, 'adminapp/admin_users.html', context)

@login_required
def block_user(request, user_id):
    try:
        user = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return redirect('admin_users')
    user.is_active = False
    user.save()
    return redirect('admin_users')  

@login_required
def unblock_user(request, user_id):
    try:
        user = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return redirect('admin_users')
    user.is_active = True
    user.save()
    return redirect('admin_users')


#------------------------------Orders---------------------------

@login_required
def admin_orders(request):
    orders = Order.objects.all()
    statuses=Order.STATUS

    context = {
        'orders': orders,
        'statuses':statuses
    }
    return render(request, 'adminapp/admin_orders.html', context)

@login_required
def manage_orders(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('order_status')

        if new_status == 'Cancelled' and order.status != 'Cancelled':
            
            order_products = OrderProduct.objects.filter(order=order)
            for order_product in order_products:
                product = order_product.product
                product.quantity += order_product.quantity
                product.save()
        elif new_status != 'Cancelled' and order.status == 'Cancelled':
            
            order_products = OrderProduct.objects.filter(order=order)
            for order_product in order_products:
                product = order_product.product
                product.quantity -= order_product.quantity
                product.save()

        
        order.status = new_status
        order.save()

        return redirect('admin_orders')

    context = {
        'order': order,
    }
    return render(request, 'adminapp/manage_orders.html', context)

#------------------------------Coupons---------------------------------

@login_required
def admin_coupons(request):
    coupons = Coupon.objects.all()
    context = {
        'coupons' : coupons
    }
    return render(request, 'adminapp/admin_coupons.html', context)


@login_required
def admin_banners(request):
    return render(request, 'adminapp/admin_banners.html')