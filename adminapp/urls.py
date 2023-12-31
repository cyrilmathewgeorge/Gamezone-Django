from django.urls import path
from adminapp import views


urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    #----------------------Product-----------------------------------
    
    path('admin_products/', views.admin_products, name='admin_products'),
    path('add_product/',views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('soft_delete_product/<int:product_id>/', views.soft_delete_product, name='soft_delete_product'),
    path('undo_soft_delete_product/<int:product_id>/', views.undo_soft_delete_product, name='undo_soft_delete_product'),
    #------------------------Varients------------------------------------
    
    path('admin_varients/', views.admin_varients, name='admin_varients'),
    path('add_varients/', views.add_varients, name='add_varients'),
    path('delete_varient/<int:varient_id>/', views.delete_varient, name='delete_varient'),
    #------------------------Category----------------------------------------
    
    path('admin_category/', views.admin_category, name='admin_category'),
    path('add_category/', views.add_category, name='add_category'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('soft_delete_category/<int:category_id>/', views.soft_delete_category, name='soft_delete_category'),
    path('undo_soft_delete_category/<int:category_id>/', views.undo_soft_delete_category, name='undo_soft_delete_category'),
    #------------------------User--------------------------------------------
    
    path('admin_users/', views.admin_users, name='admin_users'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),
    #--------------------------Orders----------------------------------------
    
    path('admin_orders/', views.admin_orders, name='admin_orders'),
    path('manage_orders//<int:order_id>/', views.manage_orders, name='manage_orders'),
    path('admin_order_details/<int:order_id>/', views.admin_order_details, name='admin_order_details'),
   
    #--------------------------Coupons----------------------------------------
    path('admin_coupons/', views.admin_coupons, name='admin_coupons'),
    path('add_coupons/', views.add_coupons, name='add_coupons'),
    path('edit_coupons/<int:coupon_id>/', views.edit_coupons, name='edit_coupons'),
    path('delete_coupons/<int:coupon_id>/', views.delete_coupons, name='delete_coupons'),
    
    #---------------------------Banners-----------------------------------------
    
    path('admin_banners/', views.admin_banners, name='admin_banners'),
    path('add_banners/', views.add_banners, name='add_banners'),
    path('edit_banners/<int:carousel_id>/', views.edit_banners, name='edit_banners'),
    path('delete_banners/<int:carousel_id>/', views.delete_banners, name='delete_banners'),
    
    #---------------------------Reviews------------------------------------------
    
    path('admin_reviews/', views.admin_reviews, name='admin_reviews'),
    path('admin_reply_review/<int:review_id>/', views.admin_reply_review, name='admin_reply_review'),

    ]