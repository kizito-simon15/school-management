from django import forms
from .models import StudentClass

class MoveStudentsForm(forms.Form):
    from_class = forms.ModelChoiceField(queryset=StudentClass.objects.all(), label='From Class')
    to_class = forms.ModelChoiceField(queryset=StudentClass.objects.all(), label='To Class')

class DeleteStudentsForm(forms.Form):
    class_to_delete = forms.ModelChoiceField(queryset=StudentClass.objects.all(), label='Class to Delete Students From')
