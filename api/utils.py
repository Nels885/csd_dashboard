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


def thermal_chamber_use(temp=None):
    now = timezone.now()
    if ThermalChamber.objects.filter(active=True):
        ThermalChamber.objects.filter(created_at__lt=now.date(), active=True).update(active=False)
    therms = ThermalChamber.objects.filter(active=True)
    if therms and temp and float(temp[:-2]) < 0:
        therms.filter(operating_mode='FROID', start_time__isnull=True).update(start_time=now)
    elif therms and temp and float(temp[:-2]) > 40:
        therms.filter(operating_mode='CHAUD', start_time__isnull=True).update(start_time=now)
    elif therms and temp:
        therms.filter(start_time__isnull=False).update(stop_time=now, active=False)
