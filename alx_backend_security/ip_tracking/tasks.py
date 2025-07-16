from celery import shared_task
from django.utils.timezone import now, timedelta
from .models import RequestLog, SuspiciousIP

SENSITIVE_PATHS = ['/login', '/admin']

@shared_task
def detect_suspicious_ips():
    one_hour_ago = now() - timedelta(hours=1)
    logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    # Count requests by ip
    ip_counts = {}
    for log in logs:
        ip_counts[log.ip_address] = ip_counts.get(log.ip_address, 0) + 1

        # Check for sensitive path access
        if any(sensitive in log.path for sensitive in SENSITIVE_PATHS):
            SuspiciousIP.objects.get_or_create(
                ip_address=log.ip_address,
                reason="Accessed sensitive path: {}".format(log.path)
            )

    # Flag IPs exceeding 100 requests/hour
    for ip, count in ip_counts.items():
        if count > 100:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip,
                reason="Exceeded 100 requests in an hour"
            )
