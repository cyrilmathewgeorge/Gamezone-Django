from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from . import verify
import re
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
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
            auth.login(request, user)
            messages.success(request, 'You are now logged in. ')
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

@login_required
def logout(request):
    auth.logout(request)  
    return redirect('login')