from django.urls import path
from . import views
urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_success/<int:id>/', views.order_success, name='order_success'),
    path('confirm_razorpay_payment/<str:order_number>/', views.confirm_razorpay_payment, name='confirm_razorpay_payment'),
    
    
]
