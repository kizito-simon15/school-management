from django.urls import path
from updations import views

urlpatterns = [
    path('move-students/', views.move_students, name='move_students'),
    path('delete-students/', views.delete_students, name='delete_students'),
    path('move-students/success/', views.move_students_success, name='move_students_success'),
    path('delete-students/success/', views.delete_students_success, name='delete_students_success'),
]
