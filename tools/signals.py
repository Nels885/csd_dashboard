from django.db.models.signals import pre_save
from django.utils import timezone
from django.dispatch import receiver
from constance import config

from .models import BgaTime, ThermalChamberMeasure


@receiver(pre_save, sender=BgaTime)
def pre_save_bga_time(sender, instance, **kwargs):
    if instance.start_time and instance.end_time:
        start = timezone.datetime.combine(instance.date, instance.start_time)
        end = timezone.datetime.combine(instance.date, instance.end_time)
        instance.duration = (end - start).seconds


@receiver(pre_save, sender=ThermalChamberMeasure)
def pre_save_thermal_chamber_measure(sender, instance, **kwargs):
    if instance.value:
        volts = instance.value / 1023
        instance.temp = "{:.1f}°C".format(((volts - 0.5) * 100) + config.MQTT_TEMP_ADJ)
