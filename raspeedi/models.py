from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Raspeedi(models.Model):
    ref_boitier = models.BigIntegerField(primary_key=True)
    produit = models.CharField(max_length=20)
    facade = models.CharField(max_length=2)
    type = models.CharField(max_length=3)
    dab = models.BooleanField(default=False)
    cam = models.BooleanField(default=False)
    dump_peedi = models.CharField(max_length=25, null=True)
    cd_version = models.CharField(max_length=10, null=True)
    media = models.CharField(max_length=20, null=True)
    carto = models.CharField(max_length=20, null=True)
    dump_renesas = models.CharField(max_length=50, null=True)
    ref_mm = models.CharField(max_length=200, null=True)
    connecteur_ecran = models.IntegerField(null=True)


class AddReference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    produit_ajoute = models.ForeignKey(Raspeedi, on_delete=models.CASCADE)
    ajoute_le = models.DateTimeField(auto_now_add=True)
