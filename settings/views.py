from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Profile, OpeningHours
from .forms import PersonalInformationForm, EmployeeForm, OpeningHoursForm


def user_is_owner(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile.position == 'Owner'


@login_required
def settings(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PersonalInformationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = request.user
                    user.first_name = form.cleaned_data.get('first_name', '')
                    user.email = form.cleaned_data.get('email', '')
                    user.save()
                    
                    profile.phone = form.cleaned_data.get('phone', '')
                    profile.dob = form.cleaned_data.get('dob')
                    profile.position = form.cleaned_data.get('position', '')
                    profile.save()

                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('settings')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'email': request.user.email,
            'phone': profile.phone,
            'dob': profile.dob,
            'position': profile.position,
        }
        form = PersonalInformationForm(initial=initial_data)

    context = {
        'form': form,
        'active_tab': 'personal',
        'profile': profile,
    }
    return render(request, 'settings.html', context)



@login_required
def upload_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.avatar = request.FILES['avatar']
        profile.save()
        return JsonResponse({'success': True, 'avatar_url': profile.avatar.url})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def opening_hours(request):
    open_hours = OpeningHours.objects.order_by('id')
    selected_hour = None
    form = None
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            if not user_is_owner(request.user):
                messages.error(request, 'Only Owner users can delete opening hours.')
            else:
                hour_id = request.POST.get('hour_id')
                if hour_id:
                    try:
                        OpeningHours.objects.get(id=hour_id).delete()
                        messages.success(request, 'Opening hours deleted successfully.')
                    except OpeningHours.DoesNotExist:
                        messages.error(request, 'Opening hours record not found.')
            return redirect('settings_hours')

        hour_id = request.POST.get('hour_id')
        instance = None
        if hour_id:
            instance = get_object_or_404(OpeningHours, id=hour_id)
            selected_hour = instance

        form = OpeningHoursForm(request.POST, instance=instance)
        if form.is_valid():
            if not user_is_owner(request.user):
                messages.error(request, 'Only Owner users can manage opening hours.')
                return redirect('settings_hours')
            hour = form.save(commit=False)
            hour.day_of_week = form.cleaned_data['day_of_week']
            hour.save()
            if instance:
                messages.success(request, 'Opening hours updated successfully.')
            else:
                messages.success(request, 'Opening hours added successfully.')
            return redirect('settings_hours')
    else:
        hour_id = request.GET.get('hour_id')
        if hour_id:
            selected_hour = get_object_or_404(OpeningHours, id=hour_id)
        form = OpeningHoursForm(instance=selected_hour)

    context = {
        'active_tab': 'hours',
        'open_hours': open_hours,
        'form': form,
        'selected_hour': selected_hour,
        'can_manage_hours': user_is_owner(request.user),
    }
    return render(request, 'settings_hours.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated successfully.')
            return redirect('settings_password')
    else:
        form = PasswordChangeForm(request.user)
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    context = {
        'form': form,
        'active_tab': 'password',
    }
    return render(request, 'settings_password.html', context)


@login_required
def employees(request):
    if not user_is_owner(request.user):
        messages.error(request, 'Only Owner users can access employee management.')
        return redirect('settings')

    employees = User.objects.order_by('username')
    for employee in employees:
        Profile.objects.get_or_create(user=employee)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            user_id = request.POST.get('user_id')
            if user_id and str(request.user.id) != str(user_id):
                try:
                    employee = User.objects.get(id=user_id)
                    employee.delete()
                    messages.success(request, 'Employee deleted successfully.')
                except User.DoesNotExist:
                    messages.error(request, 'Employee not found.')
            else:
                messages.error(request, 'You cannot delete your own account.')
            return redirect('settings_employees')

        form = EmployeeForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    employee = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                    )
                    employee.first_name = form.cleaned_data['first_name']
                    employee.save()

                    Profile.objects.create(
                        user=employee,
                        phone=form.cleaned_data['phone'],
                        dob=form.cleaned_data['dob'],
                        position=form.cleaned_data['position'],
                    )
                messages.success(request, 'Employee created successfully.')
                return redirect('settings_employees')
            except Exception as e:
                messages.error(request, f'Unable to create employee: {str(e)}')
    else:
        form = EmployeeForm()

    context = {
        'employees': employees,
        'form': form,
        'active_tab': 'employees',
    }
    return render(request, 'settings_employees.html', context)

