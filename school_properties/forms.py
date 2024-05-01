from django import forms
from .models import Property
from apps.corecode.models import AcademicSession

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'quantity']

    def clean(self):
        cleaned_data = super().clean()
        current_session = AcademicSession.objects.filter(current=True).first()
        if not current_session:
            raise forms.ValidationError("No active session found.")
        return cleaned_data
    
# In forms.py
class UpdatePropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'quantity', 'description']
