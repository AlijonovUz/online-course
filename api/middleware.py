from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework import status

from .models import BlacklistedToken


class BlackListAccessTokenMiddleware(MiddlewareMixin):
    '''
    BlacklistedToken modeli uchun alohida middleware yozilgan bo'lib logout qilingan foydalanuvchilar access tokenlarini tekshiradi.
    Agar bazada foydalanuvchi access tokeni mavjud bo'lsa quyida keltirilgan amallarni bajarishiga to'sqinlik qiladi.

    POST, PUT, PATCH, DELETE
    '''
    def process_request(self, request):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            auth_header = request.META.get('HTTP_AUTHORIZATION', None)

            if auth_header:
                token = auth_header.split(' ')[1]

                if BlacklistedToken.objects.filter(token=token).exists():
                    return JsonResponse({
                        'data': None,
                        'error': {
                            'errorId': status.HTTP_401_UNAUTHORIZED,
                            'isFriendly': True,
                            'errorMsg': "Authentication credentials were not provided."
                        },
                        'success': False
                    }, status=status.HTTP_401_UNAUTHORIZED)

