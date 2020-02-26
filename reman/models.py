from django.db import models

from dashboard.models import UserProfile

dict_year = {
    2020: 'C', 2021: 'D', 2022: 'G', 2023: 'H', 2024: 'K', 2025: 'L', 2026: 'O', 2027: 'T', 2028: 'U',
    2029: 'V', 2030: 'W',
}


class Batch(models.Model):
    year = models.CharField("années", max_length=1)
    number = models.IntegerField("numéro de lot")
    quantity = models.IntegerField('quantité')
    created_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.year


class Repair(models.Model):
    MODEL_CHOICES = [
        ('EDC15C2', 'EDC15C2'),
        ('EDC17', 'EDC17'),
    ]
    batch_year = models.ForeignKey(Batch, related_name='batch_year', on_delete=models.CASCADE)
    batch_number = models.ForeignKey(Batch, related_name='batch_number', on_delete=models.CASCADE)
    identify_number = models.CharField("numéro d'identification", max_length=10, unique=True)
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
    repair = models.ForeignKey(Repair, related_name="comments", on_delete=models.CASCADE)
    value = models.CharField("commentaire", max_length=500)

    def __str__(self):
        return self.value
