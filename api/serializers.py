import re

from rest_framework import serializers

from .models import *


class UserSerializer(serializers.ModelSerializer):
    '''
    UserSerializer - User modelidan foydalanuvchilarni ma'lumotlarini JSON shaklida olib berish uchun ishlatiladi.
    '''

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'is_active']
        read_only_fields = ['id', 'username', 'is_active']


class CourseSerializer(serializers.ModelSerializer):
    '''
    CourseSerializer - Courses modelidan ma'lumotlarni JSON shaklida olib berish uchun ishlatiladi.
    '''

    class Meta:
        model = Courses
        fields = '__all__'
        read_only_fields = ['id']


class LessonSerializer(serializers.ModelSerializer):
    '''
    LessonSerializer - Lessons modelidan ma'lumotlarni JSON shaklida olib berish uchun ishlatiladi.

    to_representation - ushbu funksiyaga kiritilgan keylardagi to'liq ma'lumotlarni GET orqali uzatadi.
    POST, PUT, PATCH dan foydalanayotganda faqat chiqarilgan to'liq ma'lumotlarni ID si bilan murojaat qilinadi.

    Eslatma: POST, PUT, PATCH orqali ishlayotganingizda to_representation funksiaysida berilgan keylardagi to'liq ma'lumotini kiritmang! Aks holda xatolik kelib chiqadi.
    Faqat kerakli maydon ID si bilan murojaat qiling! To'liq ma'lumotlar faqat GET orqali murojaat qilinganida chiqadi.
    '''

    class Meta:
        model = Lessons
        fields = '__all__'
        read_only_fields = ['id', 'teacher', 'like', 'dislike', 'deadline']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['course'] = CourseSerializer(instance.course).data
        data['teacher'] = UserSerializer(instance.teacher).data

        return data


class LessonFileSerializer(serializers.ModelSerializer):
    '''
        LessonFileSerializer - LessonFile modelidan ma'lumotlarni JSON shaklida olib berish uchun ishlatiladi.

        to_representation - ushbu funksiyaga kiritilgan keylardagi to'liq ma'lumotlarni GET orqali uzatadi.
        POST, PUT, PATCH dan foydalanayotganda faqat chiqarilgan to'liq ma'lumotlarni ID si bilan murojaat qilinadi.

        Eslatma: POST, PUT, PATCH orqali ishlayotganingizda to_representation funksiaysida berilgan keylardagi to'liq ma'lumotini kiritmang! Aks holda xatolik kelib chiqadi.
        Faqat kerakli maydon ID si bilan murojaat qiling! To'liq ma'lumotlar faqat GET orqali murojaat qilinganida chiqadi.
        '''

    class Meta:
        model = LessonFile
        fields = '__all__'
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['lesson'] = LessonSerializer(instance.lesson).data

        return data


class CommentSerializer(serializers.ModelSerializer):
    '''
        CommentSerializer - Comments modelidan ma'lumotlarni JSON shaklida olib berish uchun ishlatiladi.

        to_representation - ushbu funksiyaga kiritilgan keylardagi to'liq ma'lumotlarni GET orqali uzatadi.
        POST, PUT, PATCH dan foydalanayotganda faqat chiqarilgan to'liq ma'lumotlarni ID si bilan murojaat qilinadi.

        Eslatma: POST, PUT, PATCH orqali ishlayotganingizda to_representation funksiaysida berilgan keylardagi to'liq ma'lumotini kiritmang! Aks holda xatolik kelib chiqadi.
        Faqat kerakli maydon ID si bilan murojaat qiling! To'liq ma'lumotlar faqat GET orqali murojaat qilinganida chiqadi.
    '''

    class Meta:
        model = Comments
        fields = '__all__'
        read_only_fields = ['id', 'author']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['lesson'] = LessonSerializer(instance.lesson).data
        data['author'] = UserSerializer(instance.author).data

        return data


class RegisterSerializer(serializers.ModelSerializer):
    '''
    RegisterSerializer - User modeli bilan birgalikda ishlaydi. Ushbu serializer faqat RegisterView uchun ishlaydi.

    Eslatma: Hech qanday ma'lumotlarni o'zgartirmang! Validatorlardagi re.match patternlari
    validatorlarga kerakli ma'lumotni tekshirish uchun ishlatilgan. (O'zgartirilmasin)
    '''
    password1 = serializers.CharField(write_only=True, min_length=8, max_length=128)
    password2 = serializers.CharField(write_only=True, min_length=8, max_length=128)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        extra_kwargs = {
            'email': {
                'required': True,
                'allow_null': False,
                'allow_blank': False
            }
        }

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.")

        if User.objects.filter(username=value):
            raise serializers.ValidationError("Username is already taken.")

        return value

    def validate_email(self, value):
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
            raise serializers.ValidationError("Invalid email entered.")
        return value

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')

        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password1')
        )

        return user
