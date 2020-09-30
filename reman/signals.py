from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.management import call_command

from .models import Repair


@receiver(post_save, sender=Repair)
def post_save_repair(sender, instance, **kwargs):
    call_command('exportreman', '--repair')
    prod_ok = Repair.objects.exclude(status="Rebut").filter(batch=instance.batch).count()
    if prod_ok >= instance.batch.quantity:
        instance.batch.active = False
    else:
        instance.batch.active = True
    instance.batch.save()
