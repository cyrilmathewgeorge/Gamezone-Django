# Generated by Django 4.2.4 on 2023-10-05 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_reviewrating'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewrating',
            name='admin_reply',
            field=models.TextField(blank=True, max_length=500),
        ),
    ]