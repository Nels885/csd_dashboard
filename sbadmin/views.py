import os

from celery.result import AsyncResult
from celery_progress.backend import Progress
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache


@never_cache
def get_progress_view(request):
    progress = Progress(AsyncResult(request.GET.get("task_id", "")))
    return JsonResponse(progress.get_info())


def download_file_view(request):
    celery_result = AsyncResult(request.GET.get("task_id", ""))
    print(celery_result)
    if isinstance(celery_result.result, dict):
        filepath = celery_result.result.get("data", {}).get("outfile", "")
        if os.path.exists(filepath):
            with open(filepath, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/ms-excel")
                outfile = os.path.basename(filepath)
                response['Content-Disposition'] = "attachment; filename=%s" % outfile
                return response
    raise Http404
