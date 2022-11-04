from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from crum import get_current_user

from utils.django.decorators import disable_for_loaddata
from .models import Repair, Batch


@receiver(post_save, sender=Repair)
@disable_for_loaddata
def post_save_repair(sender, instance, **kwargs):
    prod_ok = Repair.objects.filter(batch=instance.batch, status="Réparé").order_by('-closing_date')
    if prod_ok.count() >= instance.batch.quantity or instance.batch.active is False:
        instance.batch.active = False
        if prod_ok:
            instance.batch.closing_date = prod_ok.first().closing_date
    else:
        instance.batch.active = True
    instance.batch.save()


@receiver(pre_save, sender=Repair)
@disable_for_loaddata
def pre_save_repair(sender, instance, **kwargs):
    user = get_current_user()
    if user and user.pk:
        if not instance.pk:
            instance.created_by = user
            batch_number = instance.identify_number[:-3] + "000"
            instance.batch = Batch.objects.get(batch_number__exact=batch_number)
        if instance.status != "Réparé":
            instance.quality_control = False
        instance.modified_by = user


@receiver(pre_save, sender=Batch)
@disable_for_loaddata
def pre_save_batch(sender, instance, **kwargs):
    user = get_current_user()
    year, number, quantity = instance.year, str(instance.number), str(instance.quantity)
    instance.batch_number = year + "0" * (3 - len(number)) + number + "0" * (3 - len(quantity)) + quantity + "000"
    if user and user.pk and not instance.pk:
        instance.created_by = user
