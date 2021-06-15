from django.db.models.signals import pre_save
from django.utils import timezone
from django.dispatch import receiver

from .models import BgaTime


@receiver(pre_save, sender=BgaTime)
def pre_save_bga_time(sender, instance, **kwargs):
    if instance.start_time and instance.end_time:
        start = timezone.datetime.combine(instance.date, instance.start_time)
        end = timezone.datetime.combine(instance.date, instance.end_time)
        instance.duration = (end - start).seconds
