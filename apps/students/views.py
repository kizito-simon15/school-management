
import csv
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.http import HttpResponse
from django.urls import reverse_lazy
import csv

from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Student, StudentBulkUpload
from apps.corecode.models import StudentClass
from apps.finance.models import Invoice

class StudentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Student
    template_name = "students/student_list.html"
    permission_required = 'students.view_student'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_classes'] = StudentClass.objects.all()
        return context

class StudentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Student
    template_name = "students/student_detail.html"
    permission_required = 'students.view_student'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payments"] = Invoice.objects.filter(student=self.object)
        return context


class StudentCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Student
    fields = "__all__"
    success_message = "New student successfully added."
    permission_required = 'students.add_student'
    permission_denied_message = 'Access Denied'
    

    def get_form(self):
        form = super(StudentCreateView, self).get_form()
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 2})
        form.fields["others"].widget = widgets.Textarea(attrs={"rows": 2})
        return form

    def get_success_url(self):
        return reverse_lazy('student-list')


class StudentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Student
    fields = "__all__"
    success_message = "Record successfully updated."
    permission_required = 'students.change_student'
    permission_denied_message = 'Access Denied'
    

    def get_form(self):
        form = super(StudentUpdateView, self).get_form()
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_admission"].widget = widgets.DateInput(
            attrs={"type": "date"}
        )
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 2})
        form.fields["others"].widget = widgets.Textarea(attrs={"rows": 2})
        return form


class StudentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Student
    success_url = reverse_lazy("student-list")
    permission_required = 'students.delete_student'


class StudentBulkUploadView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = StudentBulkUpload
    template_name = "students/students_upload.html"
    fields = ["csv_file"]
    success_url = reverse_lazy("student-list")
    success_message = "Successfully uploaded students"
    permission_required = 'students.add_student'  # Adjust as needed


class DownloadCSVViewdownloadcsv(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="student_template.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "registration_number",
                "surname",
                "firstname",
                "other_names",
                "gender",
                "parent_number",
                "address",
                "current_class",
            ]
        )

        return response