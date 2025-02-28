from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def exception(exc, content):
    '''
    API error xatoliklarini chiqaradigan funksiyani ma'lumotlarini o'zgartirib qayta ishlanishi
    '''

    response = exception_handler(exc, content)

    if isinstance(response.data, dict):
        error_msg = response.data
    else:
        error_msg = {'detail': response.data}

    if isinstance(error_msg, str):
        error_msg = error_msg
    else:
        error_msg = error_msg.get('detail', error_msg)

    if response is not None:
        return Response({
            'data': None,
            'error': {
                'errorId': response.status_code,
                'isFriendly': True,
                'errorMsg': error_msg
            },
            'success': False
        }, status=response.status_code)

    return Response({
        'data': None,
        'error': {
            'errorId': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'isFriendly': False,
            'errorMsg': "Internal server error."
        },
        'success': False
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)