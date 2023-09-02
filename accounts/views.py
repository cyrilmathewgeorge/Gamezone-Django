from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from . import verify
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
            username = email.split("@")[0]
            
            if Account.objects.filter(username=username).exists():
                messages.warning(request, "Username is already taken")
                return redirect('register')
            
            if Account.objects.filter(email=email).exists():
                messages.warning(request, "Email is already taken")
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
            print('inside the if')
            del request.session["signup_user_data"]
            
            return redirect("login")

    return render(request, "accounts/signup_otp.html")

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email, password)
        user = auth.authenticate(email=email, password=password)
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

def logout(request):
    auth.logout(request)
    return redirect('login')