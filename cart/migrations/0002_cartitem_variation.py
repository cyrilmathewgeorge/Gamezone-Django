# Generated by Django 4.2.4 on 2023-09-15 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_remove_product_price_variation_price'),
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='variation',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='store.variation'),
        ),
    ]
