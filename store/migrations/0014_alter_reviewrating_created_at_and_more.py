# Generated by Django 4.2.4 on 2023-10-06 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_reviewrating_admin_reply'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewrating',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='reviewrating',
            name='updated_at',
            field=models.DateField(auto_now=True),
        ),
    ]