from django.urls import path
from . import views
urlpatterns = [
    path('register/',views.register, name='register'),
    path('login/',views.login, name='login'),
    path('logout/',views.logout, name='logout'),
    path('signup_otp/', views.signup_otp, name='signup_otp'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('forgot_otp/', views.forgot_otp, name='forgot_otp'),
    path('new_password/<int:user_id>/', views.new_password, name='new_password'),
]
