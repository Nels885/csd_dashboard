from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from crum import get_current_user

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')

    def __str__(self):
        return self.user.username


class Post(models.Model):
    title = models.CharField('titre', max_length=100)
    overview = RichTextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.pk:
            self.author = UserProfile.objects.get(user=user)
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=None, **kwargs):
    if created:
        Token.objects.create(user=instance)


class WebLink(models.Model):
    TYPE_CHOICES = [
        ('PSA', 'PSA'), ('OPEL', 'OPEL'), ('FORD', 'FORD'), ('RENAULT', 'RENAULT'), ('CLARION', 'CLARION'),
        ('AUTRES', 'AUTRES')
    ]

    title = models.CharField('titre', max_length=200)
    url = models.URLField('lien web')
    type = models.CharField('type', max_length=50, choices=TYPE_CHOICES)
    description = models.TextField('description', max_length=2000)
    thumbnail = models.ImageField(default="no-img_160x120.png", upload_to="link_thumbnail")

    def __str__(self):
        return self.title
