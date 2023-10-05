from django.db import models

# Create your models here.

class Carousel(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class CarouselImage(models.Model):
    carousel = models.ForeignKey(Carousel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='photos/banners')
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.caption or str(self.image)