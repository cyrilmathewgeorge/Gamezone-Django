# Generated by Django 4.2.4 on 2023-09-13 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_variation_refurbished_quality_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='stock',
        ),
        migrations.AddField(
            model_name='variation',
            name='stock',
            field=models.IntegerField(default=0),
        ),
    ]
