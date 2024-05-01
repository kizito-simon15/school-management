from django.urls import path
from .views import create_result, edit_results, StudentResultsView, ClassListView, ClassResultsView, SingleClassResultsView, SingleClassListView, SingleStudentResultsView

urlpatterns = [
    path("create/", create_result, name="create-result"),
    path("edit-results/", edit_results, name="edit-results"),
    path('student/<int:student_id>/', StudentResultsView.as_view(), name='student-results'),
    path('class/', ClassListView.as_view(), name='class-list'),
    path('class/results/<int:class_id>/', ClassResultsView.as_view(), name='class-results'),
    path('single/class/list', SingleClassListView.as_view(), name='single-class'),
    path('single/class/result/<int:class_id>/', SingleClassResultsView.as_view(), name='single-results'),
    path('single/student/results/<int:student_id>/', SingleStudentResultsView.as_view(), name='single-student')
]    