from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from cart.models import CartItem, Coupon
from accounts.models import Address
from .forms import OrderForm
from .models import Order, OrderProduct, Payment
import datetime
# Create your views here.
def place_order(request, total=0, quantity=0):
    current_user = request.user
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    final_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (18 * total) / 100
    final_total = total + tax
    
    
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            
            # Retrieve the coupon_discount from the session
            coupon_discount = request.session.get('coupon_discount', 0)
            final_total_with_coupon = final_total - coupon_discount
            
            
            data = form.save(commit=False)
            data.user = current_user
            data.order_total = final_total_with_coupon
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            
        
            selected_address_id = request.session.get('selected_address_id')
            
            if selected_address_id is not None:
                selected_address = Address.objects.get(pk=selected_address_id)
                data.selected_address = selected_address
                del request.session['selected_address_id']
            else:
                selected_address_id = request.POST.get('selected_address')
                selected_address = Address.objects.get(pk=selected_address_id) 
                data.selected_address = selected_address

            
            data.save()
            
                
            
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            
             # Remove the coupon_discount from the session
            if 'coupon_discount' in request.session:
                del request.session['coupon_discount']
            
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            selected_address = order.selected_address
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                
                'final_total' : final_total_with_coupon,
                'selected_address': selected_address,
            }
            return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')
        
def payments(request):
    if request.method == 'POST':
        print(request.POST)
        action = request.POST.get('action')
        selected_address_id = request.POST.get('selected_address')
        grand_total = request.POST.get('grand_total')
        print(grand_total)
        order_number = request.POST.get('order_number')
        print(order_number)  
        
        try:
            order = Order.objects.get(order_number=order_number, is_ordered=False)
        except Order.DoesNotExist:
            
            return HttpResponse("Order not found")

        if action == "Cash on Delivery":
            print('action is done')
            payment = Payment.objects.create(
                user=request.user,
                payment_method="Cash on Delivery",  
                amount_paid=grand_total,  
                status="Pending",  
            )

            
            order.payment = payment
            order.save()

            
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            for cart_item in cart_items:
                for variation in cart_item.variations.all():
                    OrderProduct.objects.create(
                        order=order,
                        payment=payment,  
                        user=request.user,
                        product=cart_item.product,
                        variation=variation,
                        product_type=variation.variation_category,  
                        quantity=cart_item.quantity,
                        product_price=cart_item.product.price,
                        ordered=True,  
                    )

                # Update the product's quantity or perform any other necessary updates
                cart_item.product.quantity -= cart_item.quantity
                cart_item.product.save()
                cart_items.delete()
            
            

            return redirect("order_success", id=order.id)
        else:
            return render(request, 'orders/payments.html')

    
def order_success(request, id):
    try:
        order = get_object_or_404(Order, id=id)
        order_products = OrderProduct.objects.filter(order=order)
        # Update the order status to 'Completed'
        order.status = 'Completed'
        order.is_ordered=True
        order.save()
        print(f"Order {order.order_number} status updated to 'Completed'")
    except Exception as e:
        # Log any exceptions that occur during the update
        print(f"Error updating order status: {str(e)}")
    context = {
        'order': order,
        'order_products': order_products,
    }
    return render(request, 'orders/success.html', context)