# Generated by Django 4.1.8 on 2024-11-12 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0024_remove_ckpost_subcategory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ckpost',
            name='category',
        ),
    ]
