from django.contrib import admin
from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'admission_number',
        'full_name',
        'course',
        'phone',
        'created_at',
    )

    search_fields = (
        'admission_number',
        'full_name',
        'user__username',
        'user__email',
    )

    list_filter = ('course',)
    readonly_fields = ('admission_number', 'created_at')
# Register your models here.
