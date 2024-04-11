from django.http import JsonResponse

from .models import RepairCloseReason


def repair_close_async(request):
    data = {"extra": False}
    reason = request.GET.get('reason', None)
    try:
        if reason:
            suptech_item = RepairCloseReason.objects.get(pk=reason)
            data["extra"] = suptech_item.extra
    except RepairCloseReason.DoesNotExist:
        pass
    return JsonResponse(data)
