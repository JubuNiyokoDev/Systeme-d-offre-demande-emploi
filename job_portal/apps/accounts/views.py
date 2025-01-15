from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import (
    CustomUserCreationForm,
    LoginForm,
    CustomUserChangeForm,
    CustomPasswordChangeForm,
)
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth import logout, update_session_auth_hash
from django.shortcuts import get_object_or_404
from apps.jobs.models import JobApplication, JobOffer


@login_required
def user_list(request):
    users = CustomUser.objects.all().order_by("username")
    return render(request, "accounts/user_list.html", {"users": users})


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Authentifier l'utilisateur avec le backend personnalisé
            authenticated_user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
            if authenticated_user is not None:
                login(request, authenticated_user)
                messages.success(request, "Inscription réussie!")
                return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_banned:
                    messages.error(request, "Votre compte a été banni.")
                    return redirect("accounts:login")
                login(request, user)
                messages.success(request, "Connexion réussie!")
                return redirect("home")
            else:
                messages.error(request, "Identifiants invalides.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Déconnexion réussie!")
    return redirect("home")


@login_required
def toggle_ban_user(request, user_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(
            request, "Vous n'avez pas la permission d'effectuer cette action."
        )
        return redirect("accounts:user_list")

    target_user = get_object_or_404(CustomUser, id=user_id)

    # Empêcher le bannissement des administrateurs et du staff
    if target_user.is_staff or target_user.is_superuser:
        messages.error(
            request, "Impossible de bannir un administrateur ou un membre du staff."
        )
        return redirect("accounts:user_list")

    # Empêcher l'auto-bannissement
    if target_user == request.user:
        messages.error(request, "Vous ne pouvez pas vous bannir vous-même.")
        return redirect("accounts:user_list")

    if target_user.is_banned:
        target_user.unban_user()
        messages.success(
            request, f"L'utilisateur {target_user.username} a été débanni avec succès."
        )
    else:
        target_user.ban_user()
        messages.success(
            request, f"L'utilisateur {target_user.username} a été banni avec succès."
        )

    return redirect("accounts:user_list")


@login_required
def profile(request):
    context = {"user": request.user}

    if request.user.is_recruiter:
        # Pour les recruteurs, afficher leurs offres publiées
        published_jobs = JobOffer.objects.filter(publisher=request.user).order_by(
            "-created_at"
        )

        context["published_jobs"] = published_jobs
    else:
        # Pour les candidats, afficher leurs candidatures
        applications = JobApplication.objects.filter(applicant=request.user).order_by(
            "-applied_at"
        )

        context["applications"] = applications

    return render(request, "accounts/profile.html", context)


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès!")
            return redirect("accounts:profile")
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, "accounts/edit_profile.html", {"form": form})


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Votre compte a été supprimé avec succès.")
        return redirect("home")
    return redirect("accounts:profile")


@login_required
def password_change(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(
                request, user
            )  # Important pour maintenir la session
            messages.success(request, "Votre mot de passe a été modifié avec succès!")
            return redirect("accounts:password_change_done")
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, "accounts/password_change_form.html", {"form": form})


@login_required
def password_change_done(request):
    return render(request, "accounts/password_change_done.html")
