# from django.shortcuts import render
# from django.http import HttpResponse

# # Create your views here.
# def home(request):
#     return HttpResponse('welcome')
# def add(request):
#     return HttpResponse('this is not something new')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .models import StudentProfile,Course,Attendance,Examination,ExamResult
from .forms import StudentRegistrationForm, StudentProfileForm,CourseForm,AttendanceForm,ExaminationForm,ExamResultForm


def is_admin(user):
    return user.is_authenticated and user.is_staff


# Student registration
def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Registration successful. Please log in.'
            )
            return redirect('login')
    else:
        form = StudentRegistrationForm()

    return render(request, 'register.html', {'form': form})


# Home page
@login_required
def home(request):

    total_students = StudentProfile.objects.count()
    total_courses = Course.objects.count()
    total_examinations = Examination.objects.count()

    if request.user.is_staff:

        attendance_records = Attendance.objects.all()
        recent_students = StudentProfile.objects.select_related(
            'user'
        ).order_by('-created_at')[:5]

        total_attendance = attendance_records.count()
        present_count = attendance_records.filter(
            status='Present'
        ).count()

        absent_count = attendance_records.filter(
            status='Absent'
        ).count()

        attendance_percentage = (
            round((present_count / total_attendance) * 100, 1)
            if total_attendance else 0
        )

        dashboard_data = {
            'total_students': total_students,
            'total_courses': total_courses,
            'total_examinations': total_examinations,
            'total_attendance': total_attendance,
            'present_count': present_count,
            'absent_count': absent_count,
            'attendance_percentage': attendance_percentage,
            'recent_students': recent_students,
            'is_admin': True,
        }

    else:

        student = getattr(request.user, 'student_profile', None)

        if student:
            attendance_records = Attendance.objects.filter(
                student=student
            )

            total_attendance = attendance_records.count()
            present_count = attendance_records.filter(
                status='Present'
            ).count()

            absent_count = attendance_records.filter(
                status='Absent'
            ).count()

            attendance_percentage = (
                round((present_count / total_attendance) * 100, 1)
                if total_attendance else 0
            )

            student_exam_count = ExamResult.objects.filter(
                student=student
            ).count()

        else:
            total_attendance = 0
            present_count = 0
            absent_count = 0
            attendance_percentage = 0
            student_exam_count = 0

        dashboard_data = {
            'total_students': 1 if student else 0,
            'total_courses': total_courses,
            'total_examinations': student_exam_count,
            'total_attendance': total_attendance,
            'present_count': present_count,
            'absent_count': absent_count,
            'attendance_percentage': attendance_percentage,
            'is_admin': False,
        }

    return render(request, 'home.html', dashboard_data)
@login_required
def student_module(request):
    return render(request, 'student_module.html')


# Student records
@login_required
def student_list(request):
    if request.user.is_staff:
        students = StudentProfile.objects.select_related(
            'user'
        ).order_by('full_name')
    else:
        students = StudentProfile.objects.filter(
            user=request.user
        )

    return render(
        request,
        'student_list.html',
        {'students': students}
    )


# Add a student (admin only)
@login_required
@user_passes_test(is_admin)
def student_create(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Student added successfully.'
            )
            return redirect('student_list')
    else:
        form = StudentRegistrationForm()

    return render(
        request,
        'student_form.html',
        {'form': form, 'title': 'Register New Student'}
    )


# View student details
@login_required
def student_detail(request, pk):
    student = get_object_or_404(
        StudentProfile.objects.select_related('user'),
        pk=pk
    )

    if (
        not request.user.is_staff
        and student.user_id != request.user.id
    ):
        raise PermissionDenied

    return render(
        request,
        'student_detail.html',
        {'student': student}
    )


# Edit student details
@login_required
def student_edit(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)

    if (
        not request.user.is_staff
        and student.user_id != request.user.id
    ):
        raise PermissionDenied

    if request.method == 'POST':
        form = StudentProfileForm(
            request.POST,
            instance=student
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Student record updated successfully.'
            )
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentProfileForm(instance=student)

    return render(
        request,
        'student_form.html',
        {'form': form, 'title': 'Edit Student Record'}
    )


# Delete a student record (admin only)
@login_required
@user_passes_test(is_admin)
def student_delete(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)

    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student record deleted.')
        return redirect('student_list')

    return render(
        request,
        'student_confirm_delete.html',
        {'student': student}
    )

# Student profile
@login_required
def my_profile(request):
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': (
                request.user.get_full_name()
                or request.user.username
            )
        }
    )

    if request.method == 'POST':
        form = StudentProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('my_profile')
    else:
        form = StudentProfileForm(instance=profile)

    edit_mode = request.GET.get('edit') == '1'

    return render(request, 'my_profile.html', {
        'form': form,
        'profile': profile,
        'edit_mode': edit_mode,
    })


# Login
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm(request)

    return render(request, 'login.html', {'form': form})


# Logout
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

    return redirect('home')

@login_required
def courses_module(request):
    return render(request, 'module_placeholder.html', {
        'title': 'Course Management',
        'description': 'View and manage courses offered by Hyipro.'
    })


@login_required
def attendance_module(request):
    return render(request, 'module_placeholder.html', {
        'title': 'Attendance Management',
        'description': 'View and manage student attendance.'
    })


@login_required
def examinations_module(request):
    return render(request, 'module_placeholder.html', {
        'title': 'Examination Management',
        'description': 'View and manage examinations and results.'
    })


@login_required
def courses_module(request):
    courses = Course.objects.all().order_by('course_name')
    return render(request, 'course_list.html', {
        'courses': courses,
    })


@login_required
@user_passes_test(is_admin)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully!')
            return redirect('courses_module')
    else:
        form = CourseForm()

    return render(request, 'course_form.html', {
        'form': form,
        'title': 'Add New Course',
    })


@login_required
@user_passes_test(is_admin)
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('courses_module')
    else:
        form = CourseForm(instance=course)

    return render(request, 'course_form.html', {
        'form': form,
        'title': 'Edit Course',
    })


@login_required
@user_passes_test(is_admin)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('courses_module')

    return render(request, 'course_confirm_delete.html', {
        'course': course,
    })

@login_required
def attendance_module(request):

    selected_date = request.GET.get('date')

    # Administrator can view all attendance records
    if request.user.is_staff:

        records = Attendance.objects.select_related(
            'student'
        ).all()

        if selected_date:
            records = records.filter(date=selected_date)

        total_records = records.count()
        present_count = records.filter(status='Present').count()
        absent_count = records.filter(status='Absent').count()
        late_count = records.filter(status='Late').count()

        return render(request, 'attendance_list.html', {
            'records': records,
            'selected_date': selected_date,
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'is_admin': True,
        })

    # Student can view only their own attendance
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('home')

    records = Attendance.objects.filter(
        student=student
    ).order_by('-date')

    if selected_date:
        records = records.filter(date=selected_date)

    total_records = records.count()
    present_count = records.filter(status='Present').count()
    absent_count = records.filter(status='Absent').count()
    late_count = records.filter(status='Late').count()

    percentage = (
        (present_count / total_records) * 100
        if total_records > 0 else 0
    )

    return render(request, 'student_attendance.html', {
        'records': records,
        'total_records': total_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'percentage': round(percentage, 2),
        'selected_date': selected_date,
        'is_admin': False,
    })

@login_required
@user_passes_test(is_admin)
def attendance_create(request):

    if request.method == 'POST':
        form = AttendanceForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Attendance marked successfully!'
            )
            return redirect('attendance_module')

    else:
        form = AttendanceForm()

    return render(request, 'attendance_form.html', {
        'form': form,
        'title': 'Mark Attendance'
    })


@login_required
@user_passes_test(is_admin)
def attendance_edit(request, pk):

    record = get_object_or_404(Attendance, pk=pk)

    if request.method == 'POST':
        form = AttendanceForm(
            request.POST,
            instance=record
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Attendance updated successfully!'
            )
            return redirect('attendance_module')

    else:
        form = AttendanceForm(instance=record)

    return render(request, 'attendance_form.html', {
        'form': form,
        'title': 'Edit Attendance'
    })


@login_required
@user_passes_test(is_admin)
def attendance_delete(request, pk):

    record = get_object_or_404(Attendance, pk=pk)

    if request.method == 'POST':
        record.delete()

        messages.success(
            request,
            'Attendance record deleted successfully!'
        )

        return redirect('attendance_module')

    return render(request, 'attendance_confirm_delete.html', {
        'record': record
    })

# View all examinations
@login_required
def examination_module(request):
    examinations = Examination.objects.select_related(
        'course'
    ).all().order_by('exam_date')

    selected_date = request.GET.get('date')

    if selected_date:
        examinations = examinations.filter(exam_date=selected_date)

    return render(request, 'examination_list.html', {
        'examinations': examinations,
        'selected_date': selected_date,
    })


# Add examination
@login_required
@user_passes_test(is_admin)
def examination_create(request):
    if request.method == 'POST':
        form = ExaminationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Examination added successfully!')
            return redirect('examination_module')
    else:
        form = ExaminationForm()

    return render(request, 'examination_form.html', {
        'form': form,
        'title': 'Add New Examination'
    })


# Edit examination
@login_required
@user_passes_test(is_admin)
def examination_edit(request, pk):
    examination = get_object_or_404(Examination, pk=pk)

    if request.method == 'POST':
        form = ExaminationForm(request.POST, instance=examination)

        if form.is_valid():
            form.save()
            messages.success(request, 'Examination updated successfully!')
            return redirect('examination_module')
    else:
        form = ExaminationForm(instance=examination)

    return render(request, 'examination_form.html', {
        'form': form,
        'title': 'Edit Examination'
    })


# Delete examination
@login_required
@user_passes_test(is_admin)
def examination_delete(request, pk):
    examination = get_object_or_404(Examination, pk=pk)

    if request.method == 'POST':
        examination.delete()
        messages.success(request, 'Examination deleted successfully!')
        return redirect('examination_module')

    return render(request, 'examination_confirm_delete.html', {
        'examination': examination
    })

# View results for a particular examination
@login_required
def exam_results(request, pk):
    examination = get_object_or_404(Examination, pk=pk)

    results = ExamResult.objects.filter(
        examination=examination
    ).select_related('student')

    return render(request, 'exam_results.html', {
        'examination': examination,
        'results': results,
    })


# Add student result
@login_required
@user_passes_test(is_admin)
def result_create(request, pk):
    examination = get_object_or_404(Examination, pk=pk)

    if request.method == 'POST':
        form = ExamResultForm(request.POST, examination=examination)

        if form.is_valid():
            result = form.save(commit=False)
            result.examination = examination
            result.save()

            messages.success(request, 'Result added successfully!')
            return redirect('exam_results', pk=pk)
    else:
        form = ExamResultForm(examination=examination)

    return render(request, 'exam_results_form.html', {
        'form': form,
        'examination': examination,
        'title': 'Add Student Result'
    })


# Edit student result
@login_required
@user_passes_test(is_admin)
def result_edit(request, pk):
    result = get_object_or_404(ExamResult, pk=pk)

    if request.method == 'POST':
        form = ExamResultForm(
            request.POST,
            instance=result,
            examination=result.examination
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Result updated successfully!')
            return redirect('exam_results', pk=result.examination.pk)
    else:
        form = ExamResultForm(
            instance=result,
            examination=result.examination
        )

    return render(request, 'exam_result_form.html', {
        'form': form,
        'examination': result.examination,
        'title': 'Edit Student Result'
    })


# Delete student result
@login_required
@user_passes_test(is_admin)
def result_delete(request, pk):
    result = get_object_or_404(ExamResult, pk=pk)
    examination_id = result.examination.pk

    if request.method == 'POST':
        result.delete()
        messages.success(request, 'Result deleted successfully!')
        return redirect('exam_results', pk=examination_id)

    return render(request, 'exam_result_confirm_delete.html', {
        'result': result
    })

# Account Security Module

@login_required
def account_security(request):
    return render(request, 'account_security.html', {
        'user': request.user,
    })


# Change Password
@login_required
def change_password(request):

    if request.method == 'POST':
        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():
            user = form.save()

            # Keep the user logged in after password change
            update_session_auth_hash(request, user)

            messages.success(
                request,
                'Your password has been changed successfully!'
            )

            return redirect('account_security')

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {
        'form': form,
    })
