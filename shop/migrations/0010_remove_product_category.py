# Generated by Django 4.2.22 on 2025-06-09 17:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_alter_product_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
    ]
