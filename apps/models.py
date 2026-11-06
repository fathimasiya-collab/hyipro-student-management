import uuid

from django.db import models
from django.contrib.auth.models import User


# student module
class StudentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    admission_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    full_name = models.CharField(max_length=100)

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    phone = models.CharField(max_length=15, blank=True)

    course = models.CharField(max_length=100, blank=True)

    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.admission_number:
            self.admission_number = (
                'STU' + uuid.uuid4().hex[:8].upper()
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.admission_number} - {self.full_name}"


# course module
class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"

    
# attendance module
class Attendance(models.Model):

    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
    ]

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Present'
    )

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date', 'student']

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"

# examination module
class Examination(models.Model):
    exam_name = models.CharField(max_length=100)

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='examinations'
    )

    exam_date = models.DateField()
    total_marks = models.PositiveIntegerField(default=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.exam_name} - {self.course.course_name}"

    # examresult
class ExamResult(models.Model):
    examination = models.ForeignKey(
        Examination,
        on_delete=models.CASCADE,
        related_name='results'
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='exam_results'
    )

    secured_marks = models.PositiveIntegerField()

    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ('examination', 'student')

    def __str__(self):
        return f"{self.student} - {self.examination} - {self.secured_marks}"