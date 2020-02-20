from django.db import models
from django.contrib.auth.models import User
from crum import get_current_user

from squalaetp.models import Xelon


class TagXelon(models.Model):
    xelon = models.CharField(max_length=10)
    comments = models.CharField('commentaires', max_length=400, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk:
            self.created_by = user
        super(TagXelon, self).save(*args, **kwargs)
