from django.db import models
from accounts.models import Account, Address
from store.models import Product, Variation
from django.utils import timezone
# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.payment_id
    
    
class Order(models.Model):
    STATUS =(
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
    )
    user=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    order_number = models.CharField(max_length=20)
    order_total = models.FloatField()
    tax=models.FloatField(null=True)
    status=models.CharField(max_length=10, choices=STATUS, default='New')
    ip =  models.CharField(blank=True,max_length=20)
    is_ordered=models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now,)
    updated_at=models.DateTimeField(default=timezone.now,)
    selected_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    discount=models.FloatField(null=True)
    paymenttype=models.CharField(null=True)
    
    def __str__(self):
        return self.user.first_name
    
class OrderProduct(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation=models.ForeignKey(Variation,on_delete=models.CASCADE)
    product_type=models.CharField(max_length=20)
    quantity=models.IntegerField()
    product_price=models.FloatField()
    ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.product.product_name