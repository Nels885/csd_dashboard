from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CorvetProduct, Corvet, Multimedia, Ecu


@receiver(post_save, sender=Corvet)
def post_save_corvet(sender, created, instance, **kwargs):
    default = {}
    if instance.electronique_14x.isdigit():
        default.update({"btel": Multimedia.objects.filter(hw_reference=instance.electronique_14x).first()})
    if instance.electronique_14f.isdigit():
        default.update({"radio": Multimedia.objects.filter(hw_reference=instance.electronique_14f).first()})
    if instance.electronique_14b.isdigit():
        default.update({"bsi": Ecu.objects.filter(comp_ref__startswith=instance.electronique_14b, type='BSI').first()})
    if instance.electronique_14l.isdigit():
        default.update({"emf": Ecu.objects.filter(comp_ref__startswith=instance.electronique_14l, type='EMF').first()})
    if instance.electronique_14a.isdigit():
        default.update({"cmm": Ecu.objects.filter(comp_ref__startswith=instance.electronique_14a, type='CMM').first()})
    if instance.electronique_16b.isdigit():
        default.update({"bsm": Ecu.objects.filter(comp_ref__startswith=instance.electronique_16b, type='BSM').first()})
    if instance.electronique_16p.isdigit():
        default.update({"hdc": Ecu.objects.filter(comp_ref__startswith=instance.electronique_16p, type='HDC').first()})
    CorvetProduct.objects.update_or_create(corvet=instance, defaults=default)
