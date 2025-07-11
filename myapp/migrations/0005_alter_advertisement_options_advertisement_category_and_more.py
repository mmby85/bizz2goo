# Generated by Django 5.1.6 on 2025-05-07 07:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_advertisement_alter_category_name_alter_post_time'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='advertisement',
            options={'ordering': ['position', 'category', 'display_order', '-created_at']},
        ),
        migrations.AddField(
            model_name='advertisement',
            name='category',
            field=models.ForeignKey(blank=True, help_text='Optional: Show this ad ONLY when this category is active (for sidebar ads).', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='advertisements', to='myapp.category'),
        ),
        migrations.AddField(
            model_name='advertisement',
            name='display_order',
            field=models.IntegerField(default=0, help_text='Order of display for multiple ads in the same position/category (lower numbers first).'),
        ),
        migrations.AddField(
            model_name='advertisement',
            name='position',
            field=models.CharField(choices=[('sidebar', 'Sidebar Ad (Vertical)'), ('bottom_banner_home', 'Bottom Banner Home (Horizontal)')], default='sidebar', help_text='Where this ad will be displayed.', max_length=50),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='image',
            field=models.ImageField(help_text='Image for the advertisement.', upload_to='ads/'),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Is this ad currently active and should be displayed?'),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='title',
            field=models.CharField(help_text="Internal title for the ad (e.g., 'Sidebar Ad for Tech Category').", max_length=200),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='url',
            field=models.URLField(blank=True, help_text='Optional: URL the ad links to if clickable.', null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='time',
            field=models.CharField(blank=True, default='07 May 2025', max_length=100),
        ),
    ]
