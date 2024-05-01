from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import HttpResponseRedirect
from django.contrib import messages
from django.forms import widgets
from .models import Staff

class StaffListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Staff
    template_name = 'staffs/staff_list.html'
    context_object_name = 'staff_list'
    permission_required = 'staffs.view_staff'  # Permission to view staff details
    permission_denied_message = "Access Denied"

class StaffDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Staff
    template_name = 'staffs/staff_detail.html'
    permission_required = 'staffs.view_staff'  # Permission to view staff details
    permission_denied_message = "Access Denied"

class StaffCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Staff
    fields = '__all__'
    template_name = 'staffs/staff_form.html'
    success_message = 'New staff successfully added'
    permission_required = 'staffs.add_staff'  # Permission to add new staff
    permission_denied_message = "Access Denied"

    def get_form(self):
        """Add date picker in forms"""
        form = super().get_form()
        form.fields['date_of_birth'].widget = widgets.DateInput(attrs={'type': 'date'})
        form.fields['date_of_admission'].widget = widgets.DateInput(attrs={'type': 'date'})
        form.fields['address'].widget = widgets.Textarea(attrs={'rows': 1})
        form.fields['others'].widget = widgets.Textarea(attrs={'rows': 1})
        return form

    def form_valid(self, form):
        # Now create the corresponding Staff instance
        staff = form.save(commit=False)
        staff.user = self.request.user
        staff.save()

        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('staff-list')  # Replace with your actual success URL

class StaffUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Staff
    fields = '__all__'
    template_name = 'staffs/staff_form.html'
    success_message = 'Record successfully updated.'
    permission_required = 'staffs.change_staff'  # Permission to change staff details
    permission_denied_message = "Access Denied"

    def get_form(self):
        """Add date picker in forms"""
        form = super().get_form()
        form.fields['date_of_birth'].widget = widgets.DateInput(attrs={'type': 'date'})
        form.fields['date_of_admission'].widget = widgets.DateInput(attrs={'type': 'date'})
        form.fields['address'].widget = widgets.Textarea(attrs={'rows': 1})
        form.fields['others'].widget = widgets.Textarea(attrs={'rows': 1})
        return form

class StaffDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Staff
    success_url = reverse_lazy('staff-list')
    template_name = 'staffs/staff_confirm_delete.html'
    permission_required = 'staffs.delete_staff'  # Permission to delete staff
    permission_denied_message = "Access Denied"

