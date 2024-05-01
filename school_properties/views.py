from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PropertyForm, UpdatePropertyForm
from .models import Property
from apps.corecode.models import AcademicSession


@login_required
@permission_required('school_properties.view_property', raise_exception=True)
def property_list(request):
    current_session = AcademicSession.objects.filter(current=True).first()
    properties = Property.objects.filter(session=current_session)
    return render(request, 'property_list.html', {'properties': properties})



@login_required
@permission_required('school_properties.add_property', raise_exception=True)
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            # Set the session for the property
            current_session = AcademicSession.objects.filter(current=True).first()
            form.instance.session = current_session
            form.save()
            return redirect('property_list')
    else:
        form = PropertyForm()
    return render(request, 'add_property.html', {'form': form})



@login_required
@permission_required('school_properties.view_property', raise_exception=True)
def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    return render(request, 'property_details.html', {'property': property})

@login_required
@permission_required('school_properties.change_property', raise_exception=True)
def update_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = UpdatePropertyForm(request.POST, instance=property)
        if form.is_valid():
            form.save()
            return redirect('property_list')
    else:
        form = UpdatePropertyForm(instance=property)
    return render(request, 'update_property.html', {'form': form})


@login_required
@permission_required('school_properties.delete_property', raise_exception=True)
def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        property.delete()
        return redirect('property_list')
    return render(request, 'delete_property.html', {'property': property})

