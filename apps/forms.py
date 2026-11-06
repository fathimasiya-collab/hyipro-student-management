from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Course
from .models import StudentProfile
from .models import Attendance,Examination,ExamResult

class StudentRegistrationForm(UserCreationForm):

    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'full_name',
            'password1',
            'password2',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            StudentProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name']
            )

        return user


class StudentProfileForm(forms.ModelForm):

    class Meta:
        model = StudentProfile
        fields = [
            'full_name',
            'date_of_birth',
            'phone',
            'course',
            'address',
        ]

        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'address': forms.Textarea(
                attrs={'rows': 3}
            ),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'course_code',
            'course_name',
            'duration',
            'fee',
            'description',
        ]

        widgets = {
            'course_code': forms.TextInput(attrs={
                'placeholder': 'Enter course code'
            }),
            'course_name': forms.TextInput(attrs={
                'placeholder': 'Enter course name'
            }),
            'duration': forms.TextInput(attrs={
                'placeholder': 'Example: 2 years'
            }),
            'fee': forms.NumberInput(attrs={
                'placeholder': 'Enter course fee',
                'min': '0',
                'step': '0.01',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Enter course description',
                'rows': 4,
            }),
        }


class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance

        fields = [
            'student',
            'date',
            'status',
            'remarks',
        ]

        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control'
            }),

            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),

            'status': forms.Select(attrs={
                'class': 'form-control'
            }),

            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter remarks (optional)',
                'rows': 3
            }),
        }

class ExaminationForm(forms.ModelForm):
    class Meta:
        model = Examination
        fields = [
            'exam_name',
            'course',
            'exam_date',
            'total_marks',
            'description'
        ]

        widgets = {
            'exam_name': forms.TextInput(attrs={
                'placeholder': 'Enter examination name'
            }),
            'course': forms.Select(),
            'exam_date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'total_marks': forms.NumberInput(attrs={
                'placeholder': 'Enter total marks',
                'min': '1'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Enter examination description',
                'rows': 4
            }),
        }
class ExamResultForm(forms.ModelForm):

    class Meta:
        model = ExamResult
        fields = ['student', 'secured_marks', 'remarks']

        widgets = {
            'student': forms.Select(),
            'secured_marks': forms.NumberInput(attrs={
                'placeholder': 'Enter secured marks',
                'min': '0'
            }),
            'remarks': forms.Textarea(attrs={
                'placeholder': 'Enter remarks (optional)',
                'rows': 3
            }),
        }

    def __init__(self, *args, examination=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.examination = examination

        if examination:
            self.fields['student'].queryset = StudentProfile.objects.filter(
                course=examination.course.course_name
            )

    def clean_secured_marks(self):
        marks = self.cleaned_data['secured_marks']

        if self.examination and marks > self.examination.total_marks:
            raise forms.ValidationError(
                f"Secured marks cannot exceed {self.examination.total_marks}."
            )

        return marks