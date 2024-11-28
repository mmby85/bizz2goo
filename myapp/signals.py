from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import AuthorProfile

@receiver(post_save, sender=User)
def create_author_profile(sender, instance, created, **kwargs):
    if created and instance.is_staff:  # Vérifie si l'utilisateur est un administrateur
        AuthorProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_author_profile(sender, instance, **kwargs):
    if instance.is_staff and hasattr(instance, 'authorprofile'):
        instance.authorprofile.save()
