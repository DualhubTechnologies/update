from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('student_create/', views.student_create, name='student_create'),
    path('students_list/', views.students_list, name='students_list'),
    path('student_profile/', views.student_profile, name='student_profile'),
    path('fees/', views.fees, name='fees'),
]
