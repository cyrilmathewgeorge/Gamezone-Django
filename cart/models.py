from django.db import models
from store.models import Product, Variation
from accounts.models import Account
from orders.models import Order, OrderProduct
# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField( max_length=50, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self):
        
        return self.cart_id
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE,  null=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    variations = models.ManyToManyField(Variation,blank=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    
    
    def sub_total(self):
        
        return self.product.price * self.quantity
        
    def __unicode__(self) :
        return str(self.product)

class Coupon(models.Model):
    code = models.CharField(max_length=10, unique=True)
    discription = models.CharField(max_length=50, blank=True)
    discount = models.PositiveIntegerField(help_text="Discount percentage")
    expiration_date = models.DateField()
    is_active = models.BooleanField(default=True)

class AppliedCoupon(models.Model):
    coupon=models.ForeignKey(Coupon,on_delete=models.CASCADE)
    order=models.ForeignKey(Order,on_delete=models.CASCADE)