# Generated by Django 4.1.8 on 2024-12-12 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_alter_post_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='time',
            field=models.CharField(blank=True, default='12 December 2024', max_length=100),
        ),
    ]