# Generated by Django 4.1.8 on 2024-11-14 01:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0036_remove_ckpost_image_remove_ckpost_likes_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ckpost',
            name='slug',
        ),
    ]
