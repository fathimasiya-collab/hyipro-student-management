from django.urls import path
from . import views

urlpatterns = [
    
# first login page path
    path('', views.user_login, name='login'), 
# home dashboard
    path('home/', views.home, name='home'),         
# registration
    path('register/', views.register, name='register'),
# logout
    path('logout/', views.user_logout, name='logout'),
# pofile
    path('my-profile/', views.my_profile, name='my_profile'),
# acct security1
    path('account-security/', views.account_security, name='account_security'),
    path('change-password/', views.change_password, name='change_password'),

# student management
    path('student-module/', views.student_module, name='student_module'),
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_create, name='student_create'),
    
# course mamagement
    path('courses/', views.courses_module, name='courses_module'),
    path('courses/add/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),

# attendance management
path('attendance/', views.attendance_module, name='attendance_module'),
path('attendance/add/', views.attendance_create, name='attendance_create'),
path('attendance/<int:pk>/edit/', views.attendance_edit, name='attendance_edit'),
path('attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),

# examination management
path('examinations/', views.examination_module, name='examination_module'),
path('examinations/add/', views.examination_create, name='examination_create'),
path('examinations/<int:pk>/edit/', views.examination_edit, name='examination_edit'),
path('examinations/<int:pk>/delete/', views.examination_delete, name='examination_delete'),

# exam result
path('examinations/<int:pk>/results/', views.exam_results, name='exam_results'),
path('examinations/<int:pk>/results/add/', views.result_create, name='result_create'),
path('results/<int:pk>/edit/', views.result_edit, name='result_edit'),
path('results/<int:pk>/delete/', views.result_delete, name='result_delete'),

    path(
        'students/add/',
        views.student_create,
        name='student_create'
    ),

    path(
        'students/<int:pk>/',
        views.student_detail,
        name='student_detail'
    ),

    path(
        'students/<int:pk>/edit/',
        views.student_edit,
        name='student_edit'
    ),

    path(
        'students/<int:pk>/delete/',
        views.student_delete,
        name='student_delete'
    ),

    path(
    'student-module/',
    views.student_module,
    name='student_module'
    ),

    path('my-profile/', views.my_profile, name='my_profile'),

    
]