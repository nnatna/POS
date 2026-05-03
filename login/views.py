from django.shortcuts import render
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect


# Create your views here.
def login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            next_url = request.POST.get('next') or 'home'
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    context = {'form': form, 'next': request.GET.get('next', '')}
    return render(request, 'login.html', context)