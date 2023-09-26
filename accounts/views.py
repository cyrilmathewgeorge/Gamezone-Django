from django.shortcuts import render, redirect,get_object_or_404
from .forms import RegistrationForm, ProfileEditForm
from .models import Account
from orders.models import Order, OrderProduct
from django.contrib import messages, auth
from . import verify
import re
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import HttpResponse

from cart.views import _cart_id
from cart.models import Cart, CartItem
import requests
# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            username = email.split("@")[0]
            
            pattern = r"^\+91[6789]\d{9}$"
            
            if Account.objects.filter(username=username).exists():
                messages.warning(request, "Username is already taken")
                return redirect('register')
            
            if Account.objects.filter(phone_number=phone_number).exists():
                messages.warning(request, "Phone Number is already taken")
                return redirect('register')
            
            if Account.objects.filter(email=email).exists():
                messages.warning(request, "Email is already taken")
                return redirect('register')
            
            if password != confirm_password:
                messages.warning(request, "Passwords Deos not match")
                return redirect('register')
            
            if not re.match(pattern, phone_number):
                messages.error(request, 'Invalid number format.')
                return redirect('register')
            
            otp = verify.generate_otp()
            print("Generated OTP:", otp)
            verify.send_otp(phone_number, otp)  
            
            request.session["signup_user_data"] = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "username" : username,
                "phone_number": phone_number,
                "password": password,
                "otp": otp,
            }

            messages.success(request, 'Registration Successful')
            return redirect('signup_otp')  
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def signup_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        stored_data = request.session.get("signup_user_data")
        
        print(entered_otp, stored_data['otp'])
        
        if verify.check_otp(stored_data["phone_number"], entered_otp):
            user = Account(
                first_name=stored_data["first_name"],
                last_name=stored_data["last_name"],
                username=stored_data["username"],
                email=stored_data["email"],
                phone_number=stored_data["phone_number"]
            )
            user.set_password(stored_data["password"])
            user.is_active = True
            user.save()
            del request.session["signup_user_data"]
            
            return redirect("login")

    return render(request, "accounts/signup_otp.html")

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email, password)
        user = auth.authenticate(email=email, password=password)\
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            messages.error(request, 'Invalid email format.')
            return redirect('login')
        try:
            print(user)
        except Exception as e:
            print("Error:", e)
        if user is not None:
            try:
                cart=Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists=CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart)
                    # getting product variation by cart_id
                    product_variation=[]
                    for item in cart_item:
                        variation=item.variation.all()
                        product_variation.append(list(variation))

                    # get the cartitems from the user to access his product variation
                    cart_item=CartItem.objects.filter(user=user)
                    ex_var_list=[]
                    id=[]
                    for item in cart_item:
                        existing_variation=item.variation.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index=ex_var_list.index(pr)
                            item_id= id [index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user=user
                            item.save()

                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user=user
                                item.save()
            except:
                pass
            
            auth.login(request, user)
            messages.success(request, 'You are now logged in. ')
            url = request.META.get("HTTP_REFERER")
            # the above line will grab previous url
            try:
                query=requests.utils.urlparse(url).query
                print('query-->',query)
                # next=cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                # x.split is splitting the = line
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('index')

            return redirect('home')
        else:
            messages.error(request, 'Invalid Login Credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

def forgot_password(request):
    if request.method == 'POST':
        phone_number = request.POST['mobile']
        
        pattern = r"^\+91[6789]\d{9}$"
        
        if not re.match(pattern, phone_number):
            messages.error(request, 'Invalid  number format.')
            return redirect('forgot_password')
        try:
            user = Account.objects.get(phone_number=phone_number)
        except Account.DoesNotExist:
            messages.error(request, 'Mobile number not found.')
            return redirect('forgot_password')

        otp = verify.generate_otp()
        verify.send_otp(phone_number, otp)
        
        request.session['forgot_password_otp'] = {
            "otp" : otp,
            "phone_number" : phone_number
        }
        
        return redirect('forgot_otp')

    return render(request, 'accounts/forgot_password.html')

def forgot_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_data = request.session.get('forgot_password_otp')
        print(entered_otp, stored_data['otp'])
        
        if verify.check_otp(stored_data["phone_number"], entered_otp):
            
            user = Account.objects.get(phone_number=stored_data["phone_number"])
            
            del request.session['forgot_password_otp']
            
            # Generate the URL for the 'new_password' view with the 'user_id' parameter
            new_password_url = reverse('new_password', kwargs={'user_id': user.id})
            
            return redirect(new_password_url)  
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('forgot_otp')
        
    return render(request, 'accounts/forgot_otp.html')

def new_password(request, user_id):
    user = Account.objects.get(id=user_id)
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match. Please try again.')
            return redirect('new_password')
        else:

            user.set_password(password)
            user.save()
            
            
            
            messages.success(request, 'Password reset successfully.')
            return redirect('login')  
    context = {
        'user_id' : user_id,
    }
    return render(request, 'accounts/new_password.html', context)

# --------------------------manage profile---------------------------------------

def user_dashboard(request):
    
    return render(request, 'accounts/user_dashboard.html')

def edit_profile(request):
    user = request.user  # Get the currently logged-in user

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Profile update failed. Please correct the errors below.')
    else:
        form = ProfileEditForm(instance=user)

    context = {'form': form, 'user': user}
    return render(request, 'accounts/edit_profile.html', context)

def change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']

        user = request.user

        if not user.check_password(old_password):
            messages.error(request, 'Old password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
        else:
            user.set_password(new_password1)
            user.save()
            # Update the session to prevent the user from being logged out
            auth.update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('user_dashboard')

    return render(request, 'accounts/change_password.html')

# --------------------------manage addresses---------------------------------------
from .models import Address
def user_address(request):
    if request.method == 'POST':
        # Handle the form submission to add a new address
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2', '')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        # Create a new Address object and save it to the database
        address = Address(
            first_name=first_name,
            last_name=last_name,

            phone=phone,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            postal_code= postal_code,
            country=country,
            user=request.user  # Assuming you have implemented authentication
        )
        address.save()

        # Redirect to the manage addresses page after adding the new address
        return redirect('user_address')

    else:
        # Retrieve the existing addresses for the current user
        addresses = Address.objects.filter(user=request.user)

        context = {
            'addresses': addresses
        }
        return render(request, 'accounts/user_address.html', context)

def add_address(request):
    if request.method == 'POST':
        # Get the form fields from the POST data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        # Get the logged-in user
        user = request.user

        # Create a new Address object and set the user before saving
        address = Address(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address_line_1=address_line_1,
            #address_line_2=address_line_2,
            city=city,
            state=state,
            country=country
        )
        address.save()

        # Redirect back to the manage_addresses page
        return redirect('user_address')

    return render(request, 'accounts/add_address.html')

def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    if request.method == 'POST':
        # Get the updated values from the POST data
        address.first_name = request.POST.get('first_name')
        address.last_name = request.POST.get('last_name')
        address.email = request.POST.get('email')
        address.phone = request.POST.get('phone')
        address.address_line_1 = request.POST.get('address_line_1')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.country = request.POST.get('country')
        address.save()
        # You can add a success message here if you want
        return redirect('user_address')

    context = {
        'address': address,
        'address_id': address_id,
    }
    return render(request, 'accounts/edit_address.html', context)

def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    if request.method == 'POST':
        # Get the updated values from the POST data
        address.first_name = request.POST.get('first_name')
        address.last_name = request.POST.get('last_name')
        address.email = request.POST.get('email')
        address.phone = request.POST.get('phone')
        address.address_line_1 = request.POST.get('address_line_1')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.country = request.POST.get('country')
        address.save()
        # You can add a success message here if you want
        return redirect('user_address')

    context = {
        'address': address,
        'address_id': address_id,
    }
    return render(request, 'accounts/edit_address.html', context)

def delete_address(request, address_id):
    try:
        address = Address.objects.get(id=address_id)
        address.delete()
        # You can add a success message here if you want
    except Address.DoesNotExist:
        # Address with the given ID not found, you can handle this error accordingly
        pass
    return redirect('user_address')


#------------------------User Orders----------------------
def user_orders(request,):
    orders = Order.objects.filter(user=request.user)

    # Attach the ordered products for each order
    for order in orders:
        order.order_products = OrderProduct.objects.filter(order=order)
    context = {
        'orders': orders,

    }
    return render(request, 'accounts/user_orders.html', context)

def cancel_order_product(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if order.status != 'Cancelled':
        order.status = 'Cancelled'
        #canceled_amount = Decimal(str(order.order_total))
        order.save()

        # Increase view_count for each OrderProduct
        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            product = order_product.product
            product.quantity += order_product.quantity
            product.save()
    
    return redirect('user_orders')       

@login_required
def logout(request):
    auth.logout(request)  
    return redirect('login')