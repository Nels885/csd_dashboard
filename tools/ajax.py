from django.contrib.auth.models import Group
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from utils.django.datatables import QueryTableByArgs
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
                "extra": suptech_item.extra, "to_list": suptech_item.to_list(category),
                "cc_list": suptech_item.cc_list(category), "is_48h": suptech_item.is_48h,
                "category": category
            }
        if sup:
            suptech = Suptech.objects.get(pk=sup)
            category = request.GET.get('cat', None)
            data = {
                "to_list": suptech.to_list(category), "cc_list": suptech.cc_list(category)
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


class TagXelonViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TagXelon.objects.all()
    serializer_class = TagXelonSerializer

    def list(self, request, **kwargs):
        try:
            query = QueryTableByArgs(self.queryset,  TAG_XELON_COLUMN_LIST, 1, **request.query_params).values()
            serializer = self.serializer_class(query["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": query["draw"],
                "recordsTotal": query["total"],
                "recordsFiltered": query["count"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)


class RaspiTimeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = RaspiTime.objects.all()
    serializer_class = RaspiTimeSerializer

    def list(self, request, **kwargs):
        try:
            query = QueryTableByArgs(self.queryset,  RASPI_TIME_COLUMN_LIST, 1, **request.query_params).values()
            serializer = self.serializer_class(query["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": query["draw"],
                "recordsTotal": query["total"],
                "recordsFiltered": query["count"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)
