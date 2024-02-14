from django.contrib.auth.models import Group
from django.http import JsonResponse

from utils.django.datatables import ServerSideViewSet
from .serializers import TagXelonSerializer, TAG_XELON_COLUMN_LIST, RaspiTimeSerializer, RASPI_TIME_COLUMN_LIST

from .models import SuptechItem, BgaTime, InfotechMailingList, TagXelon, RaspiTime, Suptech

from utils.data.mqtt import MQTTClass

MQTT_CLIENT = MQTTClass()


def temp_async(request):
    data = MQTT_CLIENT.result()
    return JsonResponse(data)


def suptech_mailing_async(request):
    data = {"extra": False, "to_list": "", "cc_list": "", "is_48h": False}
    item = request.GET.get('item', None)
    sup = request.GET.get('sup', None)
    try:
        if item:
            suptech_item = SuptechItem.objects.get(pk=item)
            category = request.GET.get('cat', suptech_item.category.id)
            data = {
                "extra": suptech_item.extra, "to_list": suptech_item.to_string(category),
                "cc_list": suptech_item.cc_string(category), "is_48h": suptech_item.is_48h,
                "category": category
            }
        if sup:
            suptech = Suptech.objects.get(pk=sup)
            category = request.GET.get('cat', None)
            data = {
                "to_list": suptech.to_string(category), "cc_list": suptech.cc_string(category)
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


class TagXelonViewSet(ServerSideViewSet):
    queryset = TagXelon.objects.all()
    serializer_class = TagXelonSerializer
    column_list = TAG_XELON_COLUMN_LIST
    column_start = 1


class RaspiTimeViewSet(ServerSideViewSet):
    queryset = RaspiTime.objects.all()
    serializer_class = RaspiTimeSerializer
    column_list = RASPI_TIME_COLUMN_LIST
    column_start = 1
