from django.shortcuts import render, redirect, get_object_or_404
from cart.models import Cart, CartItem, Coupon
from accounts.models import Address
from store.models import Product, Variation
from orders.models import Order, OrderProduct, Payment
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.contrib import messages
from datetime import date
from django.contrib.auth.decorators import login_required
# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    current_user=request.user
    product = Product.objects.get(id=product_id)
    
    if product.quantity <= 0:
            messages.warning(request, 'This product is out of stock.')
            return redirect('product_detail', product_id=product_id)
    
    # if user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value=request.POST[key]
                
                try:
                    variations=Variation.objects.get(product=product, variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variations)
                except:
                    pass
        
        
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                
            if product_variation in ex_var_list:
                #increase cart item quantity
                index=ex_var_list.index(product_variation)
                item_id = id[index] 
                item = CartItem.objects.get(product=product, id=item_id)
                if item.quantity < product.quantity:
                    item.quantity +=1
                    item.save()
                else:
                    messages.warning(request, 'Product quantity in cart exceeds available quantity.')
            else:
                item=CartItem.objects.create(product=product,quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    # if the user is not authenticated
    else:
        
        
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value=request.POST[key]
                
                try:
                    variations=Variation.objects.get(product=product, variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variations)
                except:
                    pass
        
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            
            ex_var_list = []
            id = []
            
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                
            if product_variation in ex_var_list:
                #increase cart item quantity
                index=ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                if item.quantity < product.quantity:
                    item.quantity +=1
                    item.save()
                else:
                    messages.warning(request, 'Product quantity in cart exceeds available quantity.')
            else:
                item=CartItem.objects.create(product=product,quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

#------Add to cart from store -----------------------------------
def add_from_store(request, product_id):
    current_user=request.user
    product = Product.objects.get(id=product_id)
    
    if product.quantity <= 0:
        
        messages.warning(request, 'This product is out of stock.')
        return redirect('product_detail', product_id=product_id)
    
    # if user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value=request.POST[key]
                
                try:
                    variations=Variation.objects.get(product=product, variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variations)
                    
                except:
                    pass
                    
        
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                
            if product_variation in ex_var_list:
                #increase cart item quantity
                index=ex_var_list.index(product_variation)
                item_id = id[index] 
                item = CartItem.objects.get(product=product, id=item_id)
                if item.quantity < product.quantity:
                    item.quantity +=1
                    item.save()
                    messages.success(request, 'Item added to cart.')
                else:
                    messages.warning(request, 'Product quantity in cart exceeds available quantity.')
            else:
                item=CartItem.objects.create(product=product,quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
            
        return redirect('store')
    else:
        
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value=request.POST[key]
                
                try:
                    variations=Variation.objects.get(product=product, variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variations)
                except:
                    pass
        
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                
            if product_variation in ex_var_list:
                #increase cart item quantity
                index=ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                #----------------Any issue with not loged in adding quantity look at this
                #item.quantity +=1
                #item.save()
                if item.quantity < product.quantity:
                    item.quantity +=1
                    item.save()
                    messages.success(request, 'Item added to cart.')
                else:
                    messages.warning(request, 'Product quantity in cart exceeds available quantity.')
            else:
                item=CartItem.objects.create(product=product,quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
            
        return redirect('store')
    
    
    
def remove_cart(request, product_id, cart_item_id):
    product=get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity >1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user,id=cart_item_id)
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request):
    total = 0
    quantity = 0
    cart_items = []
    
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (18 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass #just ignore
      
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax'       : tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request):
    total = 0
    quantity = 0
    cart_items = []
    if request.user.is_authenticated:
        addresses = Address.objects.filter(user=request.user)
        coupons = Coupon.objects.all()
    else:
        addresses = []
        
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (18 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist: 
        pass #just ignore

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        #selected_coupon_code = request.POST.get('selected_coupon')
        request.session['selected_address_id'] = selected_address_id 
        #request.session['selected_coupon_code'] = selected_coupon_code

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax'       : tax,
        'grand_total': int(grand_total),
        'addresses': addresses,
        'coupons'  : coupons,
        }
    return render(request, "store/checkout.html", context)

def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        grand_total_str = request.POST.get('grand_total', '0')  
        grand_total = float(grand_total_str)

        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Coupon not found'})

        if not coupon.is_active:
            return JsonResponse({'status': 'error', 'message': 'Coupon is not active'})
        
        if coupon.expiration_date < date.today():
            return JsonResponse({'status': 'error', 'message': 'Coupon has expired'})
        coupon_discount = (coupon.discount / 100) * grand_total
        final_total = grand_total - int(coupon_discount)
        
        # Store the coupon_discount in the session
        request.session['coupon_discount'] = int(coupon_discount)
        
        response_data = {
            'status': 'success',
            'coupon_discount': coupon_discount,
            'final_total': final_total,
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error'})
    
    
# --------------------Ueing Ajax for Cart Increment function

