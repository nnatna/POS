from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Profile
from .forms import PersonalInformationForm

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

