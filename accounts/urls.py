from django.urls import path
from . import views
urlpatterns = [
    path('register/',views.register, name='register'),
    path('login/',views.login, name='login'),
    path('logout/',views.logout, name='logout'),
    #-----------------------OTP Handling-----------------------
    
    path('signup_otp/', views.signup_otp, name='signup_otp'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('forgot_otp/', views.forgot_otp, name='forgot_otp'),
    path('new_password/<int:user_id>/', views.new_password, name='new_password'),
    
    #---------------------User Profile----------------------
    
    path('user_dashboard/',views.user_dashboard, name='user_dashboard'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    
    #---------------------User Address----------------------
    path('user_address/', views.user_address, name='user_address'),
    path('add_address/', views.add_address, name='add_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    
    #---------------------User Orders--------------------------
    path('user_orders/', views.user_orders, name='user_orders'),
    path('cancel_order_product/<int:order_id>/', views.cancel_order_product, name='cancel_order_product'),
]
