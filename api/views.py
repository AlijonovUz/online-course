from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import generics

from .permissions import *
from .serializers import *
from .models import *


class CourseViewSet(viewsets.ModelViewSet):
    '''
    CourseViewSet - Courses modeli ustida CRUD amallarni bajarish uchun ishlaydi.

    Ushbu modelda Search, ordering filterlari ishlatilgan.

    Namuna:
        Search: http://localhost:8000/lessons/?search=Python
        Ordering: http://localhost:8000/lessons/?ordering=-id
    '''

    queryset = Courses.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id', 'name']
    ordering_fields = ['name', 'created_at']
    throttle_scope = "course"

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        return Response({
            'data': response.data,
            'error': None,
            'success': True
        }, status=status.HTTP_200_OK)


class LessonViewSet(viewsets.ModelViewSet):
    '''
    LessonViewSet - Lessons modeli ustida CRUD amallarini bajarish uchun ishlaydi.


    Ushbu modelda Search, ordering va DjangoFilterBackend filterlar ishlatilgan.

    Namuna:
        Search: http://localhost:8000/lessons/?search=Python ( ID va TITLE bo'yicha )
        Ordering: http://localhost:8000/lessons/?ordering=-id ( ID va CREATED_AT bo'yicha )
        DjangoFilterBackend: http://localhost:8000/lessons/?course=1 ( ID bo'yicha )

    like, dislike - action orqali endpoint yaratadi va detail qismida like, dislike boshishni osonlashtiradi.

    Namuna:
        Like: http://localhost:8000/lessons/1/like (Like boshish uchun ishlatiladi POST methodidan foydalaniladi xavfsizlik uchun)
        Dislike: http://localhost:8000/lessons/1/dislike (Dislike boshish uchun ishlatiladi POST methodidan foydalaniladi xavfsizlik uchun)

    Like va Dislike bosish uchun foydalanuvchidan login qilinishi talab etiladi.
    Va har bir foydalanuvchi 1 ta lesson uchun faqat 1 marta layk yoki dislike boshishi mumkin.
    Agar avval like bosilgan bolsa, va yana like bosib ko'rsa u like qaytarib olinadi.
    Agar avval like bosib dislike bosilsa, like (-1) qaytarib olinadi va dislike (+1) bosiladi. Bu jarayon huddi shunday davom etaveradi.
    '''

    queryset = Lessons.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course']
    search_fields = ['id', 'title']
    ordering_fields = ['title', 'created_at']
    throttle_scope = 'lesson'

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        lesson = self.get_object()
        user = request.user

        reaction, created = LessonReaction.objects.get_or_create(lesson=lesson, user=user)

        if not created:
            if reaction.reaction == 'like':
                lesson.like -= 1
                reaction.delete()
            else:
                lesson.dislike -= 1
                lesson.like += 1
                reaction.reaction = 'like'
                reaction.save()
        else:
            lesson.like += 1
            reaction.reaction = 'like'
            reaction.save()

        lesson.save()

        return Response({
            'data': {
                'id': int(pk),
                'like': lesson.like,
                'dislike': lesson.dislike
            },
            'error': None,
            'success': True
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def dislike(self, request, pk=None):
        lesson = self.get_object()
        user = request.user

        reaction, created = LessonReaction.objects.get_or_create(lesson=lesson, user=user)

        if not created:
            if reaction.reaction == 'dislike':
                lesson.dislike -= 1
                reaction.delete()
            else:
                lesson.like -= 1
                lesson.dislike += 1
                reaction.reaction = 'dislike'
                reaction.save()
        else:
            lesson.dislike += 1
            reaction.reaction = 'dislike'
            reaction.save()

        lesson.save()

        return Response({
            'data': {
                'id': int(pk),
                'like': lesson.like,
                'dislike': lesson.dislike
            },
            'error': None,
            'success': True
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        return Response({
            'data': response.data,
            'error': None,
            'success': True
        }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(teacher=self.request.user)
        else:
            raise serializers.ValidationError({"error": "Foydalanuvchi autentifikatsiya qilinmagan!"})


class LessonFileViewSet(viewsets.ModelViewSet):
    '''
    LessonFileViewSet - Lessons uchun istalgancha media fayllarni yuklash uchun ishlatiladi.

    Ushbu modelda Search va DjangoFilterBackend ishlatilgan.

    Namuna:
        Search: http://localhost:8000/?search=1 ( ID bo'yicha )
        DjangoFilterBackend: http://localhost:8000/?lesson=1 ( ID bo'yicha )
    '''

    queryset = LessonFile.objects.all().select_related('lesson')
    serializer_class = LessonFileSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['lesson']
    search_fields = ['id']
    throttle_scope = 'lesson-file'

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        return Response({
            'data': response.data,
            'error': None,
            'success': True
        }, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    '''
    CommentViewSet - Comments modeli ustida CRUD amallarini bajarish uchun ishlatiladi.
    Foydalanuvchilar bir-birini comment'lariga reply qilish imkoniyatiga ham ega.

    Ushbu modelda Search, Ordering va DjangoFilterBackend ishlatilgan.

    Namuna:
        Search: http://localhost:8000/?search=1 ( ID va TEXT bo'yicha )
        Ordering: http://localhost:8000/?ordering=-id ( ID va CREATED_AT bo'yicha )
        DjangoFilterBackend: http://localhost:8000/?lesson=1 ( ID bo'yicha )
    '''

    queryset = Comments.objects.all().select_related('reply', 'lesson', 'author')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lesson']
    search_fields = ['id', 'text']
    ordering_fields = ['id', 'created_at']
    throttle_scope = 'comment'

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        return Response({
            'data': response.data,
            'error': None,
            'success': True
        }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RegisterView(generics.CreateAPIView):
    '''
    RegisterView - CreateAPIView dan meros olingan holatda ishlaydi.
    User modeli uchun foydalanuvchilarni ro'yxatdan o'tkazish vazifasini bajaradi va login qilingan foydalanuvchilar
    qayta bu view dan foydalana olishmaydi. Sababi IsNotAuthenticated permissioni yozilgan.
    '''

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsNotAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'data': serializer.data,
            'error': None,
            'success': True
        }, status=status.HTTP_201_CREATED)


class LogoutView(generics.GenericAPIView):
    '''
    LogoutView - GenericAPIView dan meros olingan holatda va JWT tokenlari orqali ishlaydi.
    Login qilingan foydalanuvchilarni Hisobidan chiqarish vazifasini bajaradi. Logout qilingan foydalanuvchilarni
    refresh tokenlari blacklist ( qora ro'yxat ) ga tushiradi bu esa refresh tokendan qayta foydalanmaslik imkoniyatini beradi.
    access tokenlari esa BlacklistedToken modelida saqlanadi. Bu esa access token muddati tugashidan avval foydalanuvchidan tezlik bilan
    hisobidan chiqishga va ba'zi ruxsat etilgan CRUD amallarini bajara olmasligiga sabab bo'ladi.
    '''

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh = request.GET.get('refresh')
            token = RefreshToken(refresh)
            token.blacklist()

            access = str(request.auth)
            BlacklistedToken.objects.create(token=access)

            return Response({
                'error': None,
                'success': True
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': {
                    'errorId': status.HTTP_400_BAD_REQUEST,
                    'isFriendly': True,
                    'errorMsg': "Bad request."
                },
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
