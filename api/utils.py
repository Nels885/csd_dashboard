from rest_framework.authentication import TokenAuthentication
from django.utils import timezone

from tools.models import ThermalChamber


class TokenAuthSupportQueryString(TokenAuthentication):
    """
    Extend the TokenAuthentication class to support querystring authentication
    in the form of "http://www.example.com/?auth_token=<token_key>"
    """
    def authenticate(self, request):
        # Check if 'token_auth' is in the request query params.
        # Give precedence to 'Authorization' header.
        if 'auth_token' in request.query_params and 'HTTP_AUTHORIZATION' not in request.META:
            return self.authenticate_credentials(request.query_params.get('auth_token'))
        else:
            return super(TokenAuthSupportQueryString, self).authenticate(request)


def thermal_chamber_use(temp):
    now = timezone.now()
    if float(temp[:-2]) < -10:
        thermals = ThermalChamber.objects.filter(operating_mode='FROID', active=True, start_time__isnull=True)
        thermals.update(start_time=now)
    elif float(temp[:-2]) > 40:
        thermals = ThermalChamber.objects.filter(operating_mode='CHAUD', active=True, start_time__isnull=True)
        thermals.update(start_time=now)
