from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Courses(models.Model):
    '''
    Kurslarni saqlash uchun maxsus model
    '''

    name = models.CharField(max_length=150, unique=True, verbose_name='Nomi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Qo\'shilgan vaqti')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Kurs '
        verbose_name_plural = 'Kurslar'


class Lessons(models.Model):
    '''
    Darsliklar, berilgan uyga vazifalarni saqlash uchun maxsus model
    '''

    title = models.CharField(max_length=150, verbose_name='Sarlavhasi')
    description = models.TextField(blank=True, null=True, verbose_name='Tavsifi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Qo\'shilgan vaqti')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqti')
    is_active = models.BooleanField(default=True, verbose_name='Holati')

    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='lessons', verbose_name='Kursi')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons', verbose_name='O\'qituvchi')

    like = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Yoqtirishlar soni')
    dislike = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Yoqtirmasliklar soni')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Dars '
        verbose_name_plural = 'Darslar'
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'title'],
                name="unique_lesson_title_per_course"
            )
        ]


class LessonReaction(models.Model):
    '''
    Lessons modelidagi like, dislike lar uchun maxsus model, ushbu model API'da ko'rsatilmaydi.
    '''

    lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE, related_name='lesson_reaction')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reaction = models.CharField(max_length=7)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['lesson', 'user'],
                name="unique_lesson_reaction_per_user"
            )
        ]


class LessonFile(models.Model):
    '''
    Lessons modelidagi darsliklar uchun media fayllarni qo'shish uchun maxsus model
    '''

    lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE, related_name='lesson_files', verbose_name='Darsi')
    file = models.FileField(upload_to='lessons/', verbose_name='Fayli')

    def __str__(self):
        return f"{self.lesson.title} - {self.file.name}"

    class Meta:
        verbose_name = 'Fayl '
        verbose_name_plural = 'Fayllar'


class Comments(models.Model):
    '''
    Lessons modelidagi darsliklarga izohlar qoldirish uchun maxsus model
    '''

    text = models.TextField(verbose_name='Matni')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Qo\'shilgan vaqti')

    reply = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies', verbose_name='Javob berilgan')
    lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE, related_name='comments', verbose_name='Darsi')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comments', verbose_name='Muallifi')

    def __str__(self):
        return self.text[:20]

    class Meta:
        verbose_name = 'Izoh '
        verbose_name_plural = 'Izohlar'


class BlacklistedToken(models.Model):
    '''
    Logout qilgan foydalanuvchilarni access tokenlari saqlanadigan qora ro'yxat modeli
    '''

    token = models.CharField(max_length=500)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
