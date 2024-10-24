import numpy as np

from django.db.models.signals import pre_save
from django.utils import timezone
from django.dispatch import receiver
from constance import config

from utils.django.decorators import disable_for_loaddata
from .models import BgaTime, ThermalChamberMeasure, RaspiTime, Suptech


@receiver(pre_save, sender=BgaTime)
@disable_for_loaddata
def pre_save_bga_time(sender, instance, **kwargs):
    if instance.start_time and instance.end_time:
        start = timezone.datetime.combine(instance.date, instance.start_time)
        end = timezone.datetime.combine(instance.date, instance.end_time)
        instance.duration = (end - start).seconds


@receiver(pre_save, sender=RaspiTime)
@disable_for_loaddata
def pre_save_raspi_time(sender, instance, **kwargs):
    if instance.start_time and instance.end_time:
        start = timezone.datetime.combine(instance.date, instance.start_time)
        end = timezone.datetime.combine(instance.date, instance.end_time)
        instance.duration = (end - start).seconds


@receiver(pre_save, sender=ThermalChamberMeasure)
@disable_for_loaddata
def pre_save_thermal_chamber_measure(sender, instance, **kwargs):
    if instance.value:
        volts = instance.value / 1023
        instance.temp = "{:.1f}°C".format(((volts - 0.5) * 100) + config.MQTT_TEMP_ADJ)


@receiver(pre_save, sender=Suptech)
@disable_for_loaddata
def pre_save_suptech(sender, instance, **kwargs):
    # if instance.status == 'En Cours':
    #     instance.is_48h = False
    if instance.created_at and instance.modified_at and instance.status == "Cloturée":
        start_date = instance.created_at.strftime("%Y-%m-%d")
        end_date = instance.modified_at.strftime("%Y-%m-%d")
        instance.days_late = np.busday_count(start_date, end_date)
    # elif not instance.is_48h:
    #     instance.days_late = None
