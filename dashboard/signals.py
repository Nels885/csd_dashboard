from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from .models import UserProfile, ShowCollapse


@receiver(post_save, sender=User)
def create_user_profile(sender, created, instance, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        ShowCollapse.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=None, **kwargs):
    if created:
        Token.objects.create(user=instance)
