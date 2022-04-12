from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from utils.django.decorators import disable_for_loaddata
from .models import UserProfile, ShowCollapse


@receiver(post_save, sender=User)
@disable_for_loaddata
def create_user_profile(sender, instance=None, created=None, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        ShowCollapse.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
@disable_for_loaddata
def create_auth_token(sender, instance=None, created=None, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)
