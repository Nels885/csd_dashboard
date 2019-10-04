from django.db import models

from dashboard.models import UserProfile


class Reman(models.Model):
    MODEL_CHOICES = [
        ('EDC15C2', 'EDC15C2'),
        ('EDC17', 'EDC17'),
    ]
    batch_number = models.CharField("numéro de lot", max_length=50)
    identify_number = models.CharField("numéro d'identification", max_length=50)
    product_model = models.CharField("modèle produit", max_length=50, choices=MODEL_CHOICES)
    product_reference = models.CharField("référence produit", max_length=50)
    serial_number = models.CharField("numéro de série", max_length=100, blank=True)
    remark = models.CharField("remarques", max_length=1000, blank=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    quality_control = models.BooleanField("contrôle qualité", default=False)
    checkout = models.BooleanField("contrôle de sortie", default=False)
    closing_date = models.DateTimeField("date de cloture", null=True, blank=True)

    def __str__(self):
        return self.identify_number


class Comment(models.Model):
    reman = models.ForeignKey(Reman, related_name="comments", on_delete=models.CASCADE)
    value = models.CharField("commentaire", max_length=500)

    def __str__(self):
        return self.value
