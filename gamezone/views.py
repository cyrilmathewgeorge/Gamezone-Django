from django.shortcuts import render
from store.models import Product
from adminapp.models import Carousel
def home(request):
    products = Product.objects.all().filter(is_available=True)
    product_count = products.count()
    
    carousel = Carousel.objects.filter(is_active=True).first()
     
    context = {
        'products' : products,
        'product_count' : product_count,
        'carousel': carousel,
    }
    return render(request, 'home.html', context)