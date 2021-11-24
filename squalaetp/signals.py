import re
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Sivin, Xelon
from psa.models import Corvet


@receiver(pre_save, sender=Sivin)
def pre_save_sivin(sender, instance, **kwargs):
    try:
        if re.match(r'^[VWZ][FLR0]\w{15}$', str(instance.codif_vin)):
            instance.corvet = Corvet.objects.get(vin=instance.codif_vin)
    except Corvet.DoesNotExist as err:
        print(f"DoesNotExist: {instance} => {err}")


@receiver(pre_save, sender=Xelon)
def pre_save_xelon(sender, instance, **kwargs):
    try:
        if re.match(r'^[VWZ][FLR0]\w{15}$', str(instance.vin)):
            instance.corvet = Corvet.objects.get(vin=instance.vin)
    except Corvet.DoesNotExist:
        instance.corvet = None
