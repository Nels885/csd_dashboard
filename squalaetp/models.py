from django.db import models
from django.utils import timezone


class Xelon(models.Model):
    numero_de_dossier = models.CharField(max_length=10, unique=True)
    vin = models.CharField(max_length=17)
    modele_produit = models.CharField(max_length=50)
    modele_vehicule = models.CharField(max_length=50)
    reparer = models.BooleanField(default=False)
    ajouter_le = models.DateField(default=timezone.now)
    cloture_le =models.DateField(null=True)

    def __str__(self):
        return "{} - {} - {} - {}".format(self.numero_de_dossier, self.vin, self.modele_produit, self.modele_vehicule)
