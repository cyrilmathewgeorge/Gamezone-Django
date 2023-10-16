from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import Account, Wallet
from orders.models import Order, OrderProduct, Payment
from store.models import Product, ProductImage, Variation
from cart.models import Coupon 
from category.models import Category
from django.views.decorators.cache import cache_control, never_cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from datetime import timedelta, datetime
from django.db.models import Count, Sum
from decimal import Decimal
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
    if request.user.is_superadmin:
        if not request.user.is_superadmin:
            return redirect('index')
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        recent_orders = Order.objects.filter(is_ordered=True).order_by('-created_at')[:10]

        last_year = end_date - timedelta(days=365)
        yearly_order_counts = (
            Order.objects
            .filter(created_at__range=(last_year, end_date), is_ordered=True)
            .values('created_at__year')
            .annotate(order_count=Count('id'))
            .order_by('created_at__year')
        )

        month = end_date - timedelta(days=30)
        monthly_earnings = (
            Order.objects
            .filter(created_at__range=(month, end_date), is_ordered=True)
            .aggregate(total_order_total=Sum('order_total'))
        )['total_order_total']

        if monthly_earnings is not None:
            monthly_earnings = Decimal(monthly_earnings).quantize(Decimal('0.00'))
        else:
            monthly_earnings = Decimal('0.00')

        daily_order_counts = (
            Order.objects
            .filter(created_at__range=(start_date, end_date), is_ordered=True)
            .values('created_at__date')
            .annotate(order_count=Count('id'))
            .order_by('created_at__date')
        )
        
        dates = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in daily_order_counts]
        counts = [entry['order_count'] for entry in daily_order_counts]

        context = {
            'admin_name': request.user.first_name,
            'dates': dates,
            'counts': counts,
            'orders': recent_orders,
            'yearly_order_counts': yearly_order_counts,
            'monthly_earnings': monthly_earnings,
            'order_count': len(recent_orders),
        }

        return render(request, 'adminapp/dashboard.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to access this page.")

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
    existing_images = product.images.all() 
    
    # Set existing_category_id based on the product's category
    existing_category_id = product.category.id

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
        delete_images_ids = request.POST.getlist('delete_images')
        # Delete selected images
        for image_id in delete_images_ids:
            try:
                image_to_delete = ProductImage.objects.get(pk=image_id)
                image_to_delete.delete()
            except ProductImage.DoesNotExist:
                pass 
        if images:
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            
        return redirect('admin_products')

    context = {
        'product': product,
        'categories': categories,
        'existing_images': existing_images,
        'existing_category_id': existing_category_id,
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
@login_required
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
    
    # Soft delete related products
    Product.objects.filter(category=category).update(soft_deleted=True, is_available=False)
    
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
    
    # Undo the soft delete for related products
    Product.objects.filter(category=category).update(soft_deleted=False, is_available=True)
    
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
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
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

        if new_status == 'Rejected' and order.status != 'Rejected':
            # Handle order rejection
            order_products = OrderProduct.objects.filter(order=order)
            for order_product in order_products:
                product = order_product.product
                product.quantity += order_product.quantity
                product.save()
            
            # Update payment status to 'Refunded' and deduct the order_total from the wallet
            payment = order.payment
            if payment:
                payment.status = 'Refunded'
                payment.save()
                user_wallet = Wallet.objects.get(user=order.user)
                user_wallet.balance += Decimal(order.order_total)  # Convert to Decimal
                user_wallet.save()
        
        elif new_status != 'Rejected' and order.status == 'Rejected':
            # Transition from 'Rejected' to any other status or when new_status is not 'Rejected'
            # In either case, add the order_total to the wallet
            user_wallet = Wallet.objects.get(user=order.user)
            user_wallet.balance -= Decimal(order.order_total)  # Convert to Decimal
            user_wallet.save()
            
            if new_status != 'Rejected':
                # Handle transition from 'Rejected' to another status
                # Update payment status to 'Paid'
                payment = order.payment
                if payment:
                    payment.status = 'Paid'
                    payment.save()
        
        order.status = new_status
        order.save()

        return redirect('admin_orders')

    context = {
        'order': order,
    }
    return render(request, 'adminapp/manage_orders.html', context)

def admin_order_details(request, order_id):
    order_products = OrderProduct.objects.filter(order__user=request.user, order__id=order_id)
    orders = Order.objects.filter(is_ordered=True, id=order_id)
    
    payments = Payment.objects.filter(order__id=order_id)

    for order_product in order_products:
        order_product.total = order_product.quantity * order_product.product_price

    context = {
        'order_products': order_products,
        'orders': orders,
        'payments': payments,
    }

    return render(request, 'adminapp/admin_order_details.html', context)

#------------------------------Coupons---------------------------------
from django.utils import timezone

@login_required
def admin_coupons(request):
    coupons = Coupon.objects.all()
    # Check and update is_active based on expiration_date
    today = timezone.now().date()
    for coupon in coupons:
        if coupon.expiration_date >= today:
            coupon.is_active = True
        else:
            coupon.is_active = False
        coupon.save()
    
    context = {
        'coupons' : coupons
    }
    return render(request, 'adminapp/admin_coupons.html', context)

def add_coupons(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        discription = request.POST.get('discription')
        discount = int(request.POST.get('discount'))
        expiration_date = request.POST.get('expiration_date')
        is_active = request.POST.get('is_active') == 'on'
        
        # Convert the input expiration_date to a datetime object
        expiration_date = timezone.datetime.strptime(expiration_date, '%Y-%m-%d').date()

        # Get today's date
        today = timezone.now().date()

        if expiration_date >= today:
            coupon = Coupon.objects.create(
                code=code,
                discription=discription,
                discount=discount,
                expiration_date=expiration_date,
                is_active=is_active
            )
            return redirect('admin_coupons')
        else:
            messages.error(request, "Previous dates are not allowed for expiration. Please choose today's date or a future date.")
            return redirect('add_coupons')
        
    return render(request, 'adminapp/add_coupons.html')

def edit_coupons(request, coupon_id):
    coupon = get_object_or_404(Coupon, pk=coupon_id)
    
    if request.method == 'POST':
        coupon.code = request.POST.get('code')
        coupon.discription = request.POST.get('discription')
        coupon.discount = int(request.POST.get('discount'))
        expiration_date = request.POST.get('expiration_date')
        is_active = request.POST.get('is_active') == 'on'

        # Convert the input expiration_date to a date object
        expiration_date = timezone.datetime.strptime(expiration_date, '%Y-%m-%d').date()

        # Get today's date without the time
        today = timezone.now().date()

        if expiration_date >= today:
            coupon.expiration_date = expiration_date
            coupon.is_active = is_active
            coupon.save()
            return redirect('admin_coupons')
        else:
            messages.error(request, "Previous dates are not allowed for expiration. Please choose today's date or a future date.")
            return redirect('edit_coupons', coupon_id=coupon_id)
    context={
        'coupon' : coupon
    }
    return render(request, 'adminapp/edit_coupons.html', context)

def delete_coupons(request, coupon_id):
    try:
        coupon = Coupon.objects.get(pk=coupon_id)
    except Coupon.DoesNotExist:
        return redirect('admin_coupons')

    
    coupon.delete()
    messages.success(request, "Coupon deleted successfully.")
    return redirect('admin_coupons')

#---------------------------------Banners--------------------------
from .models import Carousel, CarouselImage
@login_required
def admin_banners(request):
    all_carousels = Carousel.objects.all()

    context = {
        'all_carousels': all_carousels,
    }
    return render(request, 'adminapp/admin_banners.html', context)

def add_banners(request):
    if request.method == 'POST':
        
        title = request.POST.get('title')
        description = request.POST.get('description_1')  
        is_active = request.POST.get('is_active')

        if is_active:
            Carousel.objects.update(is_active=False)
            
        new_carousel = Carousel.objects.create(
            title=title,
            description=description,
            is_active=is_active
        )

        
        for i in range(1, 4):  
            image_field_name = f'image_{i}'
            image = request.FILES.get(image_field_name)

            if image:
                new_image = CarouselImage(carousel=new_carousel, image=image)
                new_image.save()

        
        return redirect('admin_banners')
    
    return render(request, 'adminapp/add_banners.html')

def edit_banners(request, carousel_id):
    
    carousel = get_object_or_404(Carousel, pk=carousel_id)
    images = carousel.images.all() 
    
    if request.method == 'POST':
    
        carousel.title = request.POST['title']
        carousel.description = request.POST['description']
        is_active = request.POST.get('is_active', False)  
        
        
         # Deactivate all other banners if is_active is True
        if is_active:
            Carousel.objects.exclude(pk=carousel_id).update(is_active=False)
        
        carousel.is_active = is_active
        carousel.save() 
        # Handle images
        for image in images:
                # Update image if a new one is provided
                image.image = request.FILES.get(f'image_{image.id}', image.image)
                image.save()
        
        
        return redirect('admin_banners')
    context = {
        'carousel' : carousel,
        'images' : images,
    }
    
    return render(request, 'adminapp/edit_banners.html', context)

def delete_banners(request, carousel_id):
    
    banner = get_object_or_404(Carousel, pk=carousel_id)
    banner.images.all().delete()
    banner.delete()
    
    return redirect('admin_banners')

#--------------------------------------Reviews---------------------------
from store.models import ReviewRating

@login_required
def admin_reviews(request):
    reviews = ReviewRating.objects.all().order_by('-created_at')  
    
    context = {
        'reviews': reviews,
    }
    return render(request, 'adminapp/admin_reviews.html', context)

def admin_reply_review(request, review_id):
    if request.method == 'POST':
        admin_reply = request.POST.get('admin_reply')
        
        try:
            review = ReviewRating.objects.get(id=review_id)
            
            # Update the admin_reply field
            review.admin_reply = admin_reply
            review.save()
            
            messages.success(request, 'Reply submitted successfully.')
        except ReviewRating.DoesNotExist:
            messages.error(request, 'Review not found.')
        
        return redirect('admin_reviews') 

    return redirect('admin_reviews') 


