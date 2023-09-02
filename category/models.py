from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    discription = models.TextField(max_length=225,blank=True)
    category_images = models.ImageField(upload_to='photos/category',blank=True)
    is_available = models.BooleanField(default=True)
    soft_deleted = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        
    def save(self, *args, **kwargs):
        # Generate slug based on product name if not provided
        if not self.slug:
            self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)
        
    def get_url(self):
            return reverse('products_by_category', args=[self.slug])
        
    def __str__(self):
        return self.category_name
    
