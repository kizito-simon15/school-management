from django import forms
from django.forms import modelformset_factory

from apps.corecode.models import AcademicSession, AcademicTerm, ExamType, Subject

from .models import Result


class CreateResults(forms.Form):
    session = forms.ModelChoiceField(queryset=AcademicSession.objects.all())
    term = forms.ModelChoiceField(queryset=AcademicTerm.objects.all())
    exam = forms.ModelChoiceField(queryset=ExamType.objects.all())
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple
    )


EditResults = modelformset_factory(
    Result, fields=("test_score", "exam_score"), extra=0, can_delete=True
)

# Updated ViewResultsForm
class ViewResultsForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'test_score', 'exam_score', 'current_class']
        widgets = {
            'test_score': forms.TextInput(attrs={'placeholder': '', 'value': ''}),
            'exam_score': forms.TextInput(attrs={'placeholder': '', 'value': ''}),
        }

ViewResultsFormSet = modelformset_factory(Result, form=ViewResultsForm, extra=0)
