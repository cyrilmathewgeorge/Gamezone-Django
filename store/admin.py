from django import forms
from django.contrib import admin
from .models import Product, Variation, ReviewRating
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'modified_date', 'is_available')
    prepopulated_fields = {'slug' : ('product_name',)}
    
class VariationAdminForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = '__all__'

    VARIATION_CHOICES = (
        ('new', 'New'),
        ('refurbished_excellent', 'Refurbished Excellent'),
        ('refurbished_good', 'Refurbished Good'),
        ('refurbished_average', 'Refurbished Average'),
    )

    variation_value = forms.ChoiceField(
        choices=VARIATION_CHOICES,
        widget=forms.Select(attrs={'class': 'custom-dropdown'}),
    )

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')
    form = VariationAdminForm  # Use the custom form
    

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)