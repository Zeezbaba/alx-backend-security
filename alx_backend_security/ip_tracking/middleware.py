from django.conf import settings
from django.utils.timezone import now
from django.http import HttpResponseForbidden
from django.core.cache import cache
import requests
from .models import RequestLog, BlockedIP

# GEO_API_KEY = settings.API_KEY
# geo_api = IpGeolocationAPI(api_key=GEO_API_KEY)

def get_ip_location(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data.get('city'),
                'country': data.get('country')
            }
    except Exception:
        pass
    return {'city': None, 'country': None}

class IPTracker:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)

        # check if ip is blocked
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Access Denied!. Your IP is blocked")

        # Get location from cache or API
        geo_data = cache.get(ip)
        if not geo_data:
            geo_data = get_ip_location(ip)
            cache.set(ip, geo_data, 60 * 60 * 24)

        path = request.path
        timestamp = now()

        # save to database
        RequestLog.objects.create(
            ip_address=ip,
            timestamp=timestamp,
            path=path,
            country=geo_data['country'],
            city=geo_data['city']
            )

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()

        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
