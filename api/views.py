from rest_framework.views import APIView
from rest_framework.response import Response

from squalaetp.models import Xelon


class CharData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        labels = ["RT6/RNEG2", "SMEG", "RT4", "DISPLAY", "RNEG", "NG4"]
        prod_nb = []
        for prod in labels:
            prod_nb.append(Xelon.objects.filter(modele_produit__contains=prod).count())
        data = {
            "labels": labels,
            "default": prod_nb,
        }
        return Response(data)
