# Generated by Django 4.1.8 on 2024-11-12 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_alter_comment_time_alter_post_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='ckpost',
            name='title',
            field=models.CharField(default=1, max_length=600),
            preserve_default=False,
        ),
    ]