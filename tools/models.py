from django.db import models
from django.contrib.auth.models import User

from squalaetp.models import Xelon


class TagXelonMulti(models.Model):
    xelon = models.CharField(max_length=10)
    comments = models.CharField('commentaires', max_length=400, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
