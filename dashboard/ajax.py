from django.http import JsonResponse, Http404

from utils.data.analysis import IndicatorAnalysis, ToolsAnalysis
from utils.django.urls import reverse
from utils.django.validators import vin_psa_isvalid, immat_isvalid
from squalaetp.models import Indicator, Sivin
from squalaetp.tasks import save_sivin_to_models
from psa.models import Corvet
from psa.tasks import save_corvet_to_models
from .forms import SearchForm
from .tasks import cmd_sendemail_task


def charts_async(request):
    """
    API endpoint that allows chart data to be viewed
    """
    if request.GET.get('type') == 'prod':
        prod = Indicator.count_prods()
        data = {"prodLabels": list(prod.keys()), "prodDefault": list(prod.values())}
    elif request.GET.get('type') == 'deal':
        data = IndicatorAnalysis().new_result()
    elif request.GET.get('type') == 'suptech':
        data = ToolsAnalysis().suptech()
    else:
        data = ToolsAnalysis().use_tools()
    return JsonResponse(data)


def send_email_async(request):
    if request.user.is_staff:
        task = cmd_sendemail_task.delay("--late_products", "--pending_products", "--vin_error", "--vin_corvet")
        return JsonResponse({"task_id": task.id})
    raise Http404


def search_async(request):
    form = SearchForm(request.POST or None)
    data = {'url': reverse('dashboard:search'), 'task_id': None}
    if request.POST and form.is_valid():
        query = form.cleaned_data['query']
        select = form.cleaned_data['select']
        if query and select:
            if vin_psa_isvalid(query):
                if not Corvet.objects.filter(vin__iexact=query):
                    task = save_corvet_to_models.delay(query)
                    data['task_id'] = task.id
            elif immat_isvalid(query):
                if not Sivin.search(query):
                    task = save_sivin_to_models.delay(query)
                    data['task_id'] = task.id
            data['url'] = reverse('dashboard:search', get={'query': query, 'select': select})
    return JsonResponse(data)
