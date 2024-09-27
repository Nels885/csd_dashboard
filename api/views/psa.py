from django.db.models import Q
from django.shortcuts import redirect
from rest_framework.viewsets import ViewSet
from rest_framework import permissions, views, status
from rest_framework.response import Response

from psa.serializers import MultimediaSerializer, EcuSerializer
from psa.models import Multimedia, Ecu
from psa.ajax import download_nac_license_file

from ..utils import TokenAuthSupportQueryString


class ProductsViewSet(ViewSet):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get']

    def list(self, request):
        """
        Return a list of all users.
        """
        search = request.query_params.get('search', '')
        if search and search.isdigit():
            medias = Multimedia.objects.filter(Q(comp_ref__exact=search) | Q(label_ref__exact=search))
        else:
            medias = Multimedia.objects.filter(name__icontains=search)
        ecus = Ecu.objects.filter(Q(comp_ref__exact=search) | Q(name__icontains=search) | Q(label_ref__exact=search))
        # then we serializer the data
        projects_serializer = MultimediaSerializer(medias, many=True, context={'request': request})
        news_serializer = EcuSerializer(ecus, many=True, context={'request': request})
        data = projects_serializer.data + news_serializer.data
        return Response({'count': len(data), 'results': data})


class NacLicenseView(views.APIView):
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        update_id = request.GET.get('update')
        uin = request.GET.get('uin')
        data_type = request.GET.get('format', None)
        if update_id and uin:
            response = download_nac_license_file(update_id, uin)
            if response.status_code == 200:
                if data_type and data_type == "json":
                    return Response({'detail': 'NAC license downloaded successfully'}, status=status.HTTP_200_OK)
                return redirect(response.url)
        return Response({'error': 'Request failed'}, status=status.HTTP_404_NOT_FOUND)
