from django.contrib import admin

from .models import *


@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    actions_on_top = False
    actions_on_bottom = True


class LessonFile(admin.StackedInline):
    model = LessonFile
    extra = 1


@admin.register(Lessons)
class LessonsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    readonly_fields = ('like', 'dislike')
    search_fields = ('title',)
    actions_on_top = False
    actions_on_bottom = True

    inlines = [LessonFile]

    def get_fieldsets(self, request, obj=None):
        fields = [field.name for field in Lessons._meta.get_fields() if not field.auto_created and field.editable]
        return [("Asosiy", {'fields': fields})]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "course" or db_field.name == 'teacher':
            if Courses.objects.all().exists():
                kwargs['empty_label'] = 'Tanlang'
            elif User.objects.all().exists():
                kwargs['empty_label'] = 'Tanlang'
            else:
                kwargs['empty_label'] = "Mavjud emas"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'created_at', 'lesson')
    list_display_links = ('id', 'text')
    search_fields = ('title',)
    actions_on_top = False
    actions_on_bottom = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'reply' or db_field.name == "lesson" or db_field.name == 'author':
            if Comments.objects.all().exists():
                kwargs['empty_label'] = 'Tanlang'
            elif Lessons.objects.all().exists():
                kwargs['empty_label'] = 'Tanlang'
            elif User.objects.all().exists():
                kwargs['empty_label'] = 'Tanlang'
            else:
                kwargs['empty_label'] = "Mavjud emas"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)