from django.utils.timezone import now
from .models import RequestLog, BlockedIP

class IPTracker:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)

        # check if ip is blocked
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Access Denied!. Your IP is blocked")

        path = request.path
        timestamp = now()

        # save to database
        RequestLog.objects.create(ip_address=ip, timestamp=timestamp, path=path)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]

        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
