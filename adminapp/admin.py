from django.contrib import admin
from .models import Carousel, CarouselImage
# Register your models here.


class CarouselImageInline(admin.TabularInline):
    model = CarouselImage

class CarouselAdmin(admin.ModelAdmin):
    inlines = [CarouselImageInline]

admin.site.register(Carousel, CarouselAdmin)