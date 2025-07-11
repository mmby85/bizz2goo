# Generated by Django 5.1.6 on 2025-05-07 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_alter_advertisement_options_advertisement_category_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advertisement',
            name='url',
        ),
        migrations.AddField(
            model_name='advertisement',
            name='external_url',
            field=models.URLField(blank=True, help_text="URL externe (si 'Lien Externe Personnalisé' est choisi).", null=True),
        ),
        migrations.AddField(
            model_name='advertisement',
            name='link_type',
            field=models.CharField(choices=[('external', 'Lien Externe Personnalisé'), ('internal_form', 'Formulaire Interne (Création Société)')], default='external', help_text="Choisir si l'annonce redirige vers un lien externe ou le formulaire interne.", max_length=20),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='display_order',
            field=models.IntegerField(default=0, help_text='Order of display (lower numbers first).'),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Is this ad currently active?'),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='title',
            field=models.CharField(help_text='Internal title for the ad.', max_length=200),
        ),
    ]
