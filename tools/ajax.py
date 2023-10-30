from django.contrib.auth.models import Group
from django.http import JsonResponse

from .models import SuptechItem, BgaTime, InfotechMailingList

from utils.data.mqtt import MQTTClass

MQTT_CLIENT = MQTTClass()


def temp_async(request):
    data = MQTT_CLIENT.result()
    return JsonResponse(data)


def suptech_item_async(request):
    data = {"extra": False, "mailing_list": "", "cc_mailing_list": ""}
    try:
        if request.GET.get('pk', None):
            suptech_item = SuptechItem.objects.get(pk=request.GET.get('pk', None))
            data = {
                "extra": suptech_item.extra, "mailing_list": suptech_item.to_list(),
                "cc_mailing_list": suptech_item.cc_mailing_list,
                "is_48h": suptech_item.is_48h
            }
    except SuptechItem.DoesNotExist:
        pass
    return JsonResponse(data)


def bga_time_async(request):
    device = request.GET.get("device", None)
    status = request.GET.get("status", None)
    if device and status:
        try:
            bga_is_active = BgaTime.objects.get(name=device, end_time__isnull=True)
            bga_is_active.save(status=status)
        except BgaTime.DoesNotExist:
            pass
        if status.upper() == "START":
            BgaTime.objects.create(name=device)
        return JsonResponse({"response": "OK", "device": device, "status": status.upper()})
    return JsonResponse({"response": "ERROR"})


def infotech_mailing_async(request):
    data = {"to_list": "", "cc_list": ""}
    try:
        if request.GET.get('pk', None):
            mailing = InfotechMailingList.objects.get(pk=request.GET.get('pk', None))
            data = {
                "to_list": mailing.to_list(),
                "cc_list": mailing.cc_list()
            }
    except Group.DoesNotExist:
        pass
    return JsonResponse(data)
