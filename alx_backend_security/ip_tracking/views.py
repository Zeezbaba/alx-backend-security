from django.http import JsonResponse
from ratelimit.decorators import ratelimit
from ratelimit.exceptions import Ratelimited
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@ratelimit(key='user_or_ip', rate='10/m', block=True)
@ratelimit(key='ip', rate='5/m', block=True)

def login_view(request):
    was_limited = getattr(request, 'limits', False)

    if was_limited:
        return JsonResponse({'error': 'Too many requests'}, status=429)

    # dummy login simulation
    return JsonResponse({'message': 'Login processed'})

