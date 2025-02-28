from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    '''
    Faqat adminlarga ruxsat beruvchi qolganlarga esa SAFE_METHODS dagi methodlarga ruxsat beruvchi permission
    '''

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsNotAuthenticated(BasePermission):
    '''
    Login qilingan foydalanuvchilarni tekshirish uchun permission
    '''

    def has_permission(self, request, view):
        return not request.user.is_authenticated