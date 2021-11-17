from django.db.models.signals import pre_save
from django.dispatch import receiver

from squalaetp.models import Sivin
from psa.models import Corvet


@receiver(pre_save, sender=Sivin)
def pre_save_sivin(sender, instance, **kwargs):
    try:
        instance.corvet = Corvet.objects.get(vin=instance.codif_vin)
    except Corvet.DoesNotExist as err:
        print(f"DoesNotExist: {err}")
