from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, LoginForm
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
@login_required
def user_list(request):
    users = CustomUser.objects.all().order_by('username')
    return render(request, 'accounts/user_list.html', {'users': users})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Inscription réussie!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Connexion réussie!')
                return redirect('home')
            else:
                messages.error(request, 'Identifiants invalides.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie!')
    return redirect('home')


@login_required
def toggle_ban_user(request, user_id):
    if not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'effectuer cette action.")
        return redirect('accounts:user_list')
    
    user = get_object_or_404(CustomUser, id=user_id)
    if user.is_banned:
        user.is_banned = False
        messages.success(request, f"L'utilisateur {user.username} a été débanni.")
    else:
        user.is_banned = True
        messages.success(request, f"L'utilisateur {user.username} a été banni.")
    user.save()
    
    return redirect('accounts:user_list')