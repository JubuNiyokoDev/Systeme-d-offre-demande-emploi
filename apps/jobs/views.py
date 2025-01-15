from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from .models import JobOffer, JobApplication
from .forms import JobOfferForm, JobApplicationForm,ApplicationStatusForm
from apps.accounts.models import CustomUser
from django.core.paginator import Paginator

@login_required
def available_jobs(request):
    jobs = JobOffer.objects.filter(status='active')
    
    # Recherche par mot-clé
    query = request.GET.get('q', '')
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(description__icontains=query)
        )
    
    # Filtrage par localisation
    location = request.GET.get('location', '')
    if location and location != 'Tous les lieux':
        jobs = jobs.filter(location__iexact=location)  # Utilisation de iexact pour une correspondance exacte insensible à la casse
    
    # Filtrage par salaire
    try:
        min_salary = request.GET.get('min_salary')
        if min_salary and min_salary.isdigit():
            min_salary = int(min_salary)
            jobs = jobs.filter(salary_range__gte=min_salary)
        
        max_salary = request.GET.get('max_salary')
        if max_salary and max_salary.isdigit():
            max_salary = int(max_salary)
            jobs = jobs.filter(salary_range__lte=max_salary)
    except ValueError:
        min_salary = ''
        max_salary = ''
    
    # Filtrage par date
    date_filter = request.GET.get('date_filter')
    if date_filter:
        today = timezone.now()
        if date_filter == 'today':
            jobs = jobs.filter(created_at__date=today.date())
        elif date_filter == 'week':
            week_ago = today - timezone.timedelta(days=7)
            jobs = jobs.filter(created_at__gte=week_ago)
        elif date_filter == 'month':
            month_ago = today - timezone.timedelta(days=30)
            jobs = jobs.filter(created_at__gte=month_ago)
    
    # Filtrage par date d'expiration
    jobs = jobs.filter(
        Q(expires_at__gt=timezone.now()) |
        Q(expires_at__isnull=True)
    ).order_by('-created_at')

    # Debug des filtres
    print(f"Query: {jobs.query}")  # Affiche la requête SQL générée
    print(f"Nombre de résultats: {jobs.count()}")  # Affiche le nombre de résultats
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    # Récupération des locations uniques pour le filtre
    locations = JobOffer.objects.values_list('location', flat=True).distinct()
    
    # Préparation du contexte avec les filtres actifs
    context = {
        'jobs': jobs,
        'locations': locations,
        'query': query,
        'location': location,
        'min_salary': min_salary,
        'max_salary': max_salary,
        'date_filter': date_filter,
        'active_filters': any([
            query,
            location,
            request.GET.get('min_salary'),
            request.GET.get('max_salary'),
            date_filter
        ])
    }
    
    return render(request, 'jobs/available_jobs.html', context)

@login_required
def my_jobs(request):
    jobs = JobOffer.objects.filter(publisher=request.user).order_by('-created_at')
    return render(request, 'jobs/my_jobs.html', {'jobs': jobs})

@login_required
def job_create(request):
    if not (request.user.is_recruiter or request.user.is_staff):
        messages.error(request, "Seuls les recruteurs peuvent créer des offres d'emploi.")
        return redirect('jobs:available_jobs')
    
    if request.method == 'POST':
        form = JobOfferForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.publisher = request.user
            job.save()
            messages.success(request, "L'offre d'emploi a été créée avec succès.")
            return redirect('jobs:my_jobs')
    else:
        form = JobOfferForm()
    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Créer une offre'})

@login_required
def job_edit(request, job_id):
    job = get_object_or_404(JobOffer, id=job_id)
    
    if not (request.user.is_staff or request.user.is_superuser or job.publisher == request.user):
        messages.error(request, "Vous n'avez pas la permission de modifier cette offre.")
        return redirect('jobs:available_jobs')
    
    if request.method == 'POST':
        form = JobOfferForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "L'offre d'emploi a été mise à jour avec succès.")
            return redirect('jobs:my_jobs')
    else:
        form = JobOfferForm(instance=job)
    
    context = {
        'form': form,
        'title': f"Modifier l'offre : {job.title}",
        'job': job,
    }
    return render(request, 'jobs/job_form.html', context)

@login_required
def apply_to_job(request, job_id):
    # Vérifier si l'utilisateur est un recruteur
    if request.user.is_recruiter:
        messages.error(request, "Les recruteurs ne peuvent pas postuler aux offres d'emploi.")
        return redirect('jobs:available_jobs')
    
    job = get_object_or_404(JobOffer, id=job_id)
    
    # Vérifications
    if job.publisher == request.user:
        messages.error(request, "Vous ne pouvez pas postuler à votre propre offre.")
        return redirect('jobs:available_jobs')
    
    if job.is_expired or job.status != 'active':
        messages.error(request, "Cette offre n'est plus disponible.")
        return redirect('jobs:available_jobs')
    
    
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "Vous avez déjà postulé à cette offre.")
        return redirect('jobs:job_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Votre candidature a été envoyée avec succès!")
            return redirect('jobs:my_applications')
    
    return render(request, 'jobs/apply.html', {
        'form': JobApplicationForm(),
        'job': job
    })

@login_required
def my_applications(request):
    query = request.GET.get('q', '')
    applications = JobApplication.objects.filter(
        Q(job__title__icontains=query),
        applicant=request.user
    ).order_by('-applied_at')
    return render(request, 'jobs/my_applications.html', {'applications': applications, 'query': query})

@login_required
def job_applications(request, job_id):
    job = get_object_or_404(JobOffer, id=job_id, publisher=request.user)
    applications = job.applications.all().order_by('-applied_at')
    return render(request, 'jobs/job_applications.html', {'job': job, 'applications': applications})

# Vues pour la gestion des utilisateurs
@login_required
def user_list(request):
    if not request.user.is_staff:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('jobs:available_jobs')
    users = CustomUser.objects.all().order_by('username')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
def toggle_ban_user(request, user_id):
    if not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'effectuer cette action.")
        return redirect('accounts:user_list')
    
    user = get_object_or_404(CustomUser, id=user_id)
    if user.is_banned:
        user.unban_user()
        messages.success(request, f"L'utilisateur {user.username} a été débanni.")
    else:
        user.ban_user()
        messages.success(request, f"L'utilisateur {user.username} a été banni.")
    
    return redirect('accounts:user_list')

@login_required
def job_delete(request, job_id):
    job = get_object_or_404(JobOffer, id=job_id)
    
    # Vérifier les permissions
    if not (request.user.is_staff or request.user.is_superuser or job.publisher == request.user):
        messages.error(request, "Vous n'avez pas la permission de supprimer cette offre.")
        return redirect('jobs:available_jobs')
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, "L'offre d'emploi a été supprimée avec succès.")
        return redirect('jobs:available_jobs')
    
    return redirect('jobs:available_jobs')





@login_required
def job_detail(request, job_id):
    job = get_object_or_404(JobOffer, id=job_id)
    has_applied = False
    
    if request.user.is_authenticated and not request.user.is_recruiter:
        has_applied = JobApplication.objects.filter(
            job=job,
            applicant=request.user
        ).exists()
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'total_applications': job.applications.count(),
        'is_owner': job.publisher == request.user,
        'can_edit': request.user.is_staff or job.publisher == request.user,
    }
    
    return render(request, 'jobs/job_detail.html', context)
@login_required
def manage_applications(request, job_id=None):
    if not request.user.is_recruiter:
        messages.error(request, "Accès non autorisé.")
        return redirect('jobs:available_jobs')

    # Filtrer les offres du recruteur
    jobs = JobOffer.objects.filter(publisher=request.user)
    
    if job_id:
        job = get_object_or_404(JobOffer, id=job_id, publisher=request.user)
        applications = job.applications.all()
        context = {'job': job}
    else:
        applications = JobApplication.objects.filter(job__publisher=request.user)
        context = {}

    # Ajout du filtre par statut
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)

    # Pagination
    paginator = Paginator(applications, 10)
    page = request.GET.get('page')
    applications = paginator.get_page(page)

    context.update({
        'applications': applications,
        'jobs': jobs,
        'STATUS_CHOICES': JobApplication.STATUS_CHOICES,
    })
    
    return render(request, 'jobs/manage_applications.html', context)
@login_required
def update_application_status(request, application_id):
    if not request.user.is_recruiter:
        messages.error(request, "Accès non autorisé.")
        return redirect('jobs:available_jobs')

    application = get_object_or_404(JobApplication, 
                                  id=application_id, 
                                  job__publisher=request.user)

    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Statut de la candidature mis à jour avec succès.")
            return redirect('jobs:manage_applications')
    
    return redirect('jobs:manage_applications')

@login_required
def view_application(request, application_id):
    if not request.user.is_recruiter:
        messages.error(request, "Accès non autorisé.")
        return redirect('jobs:job_list')

    application = get_object_or_404(
        JobApplication, 
        id=application_id, 
        job__publisher=request.user
    )
    
    context = {
        'application': application,
        'form': ApplicationStatusForm(instance=application)
    }
    
    return render(request, 'jobs/view_application.html', context)

def job_list(request):
    jobs = JobOffer.objects.filter(status='active', expires_at__gt=timezone.now())
    
    # Recherche par mot-clé
    query = request.GET.get('q')
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(company__icontains=query)
        )
    
    # Filtrage par localisation
    location = request.GET.get('location')
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    # Filtrage par fourchette de salaire
    min_salary = request.GET.get('min_salary')
    max_salary = request.GET.get('max_salary')
    if min_salary:
        jobs = jobs.filter(salary_range__gte=min_salary)
    if max_salary:
        jobs = jobs.filter(salary_range__lte=max_salary)
    
    # Filtrage par date
    date_filter = request.GET.get('date_filter')
    if date_filter:
        today = timezone.now()
        if date_filter == 'today':
            jobs = jobs.filter(created_at__date=today.date())
        elif date_filter == 'week':
            jobs = jobs.filter(created_at__gte=today - timezone.timedelta(days=7))
        elif date_filter == 'month':
            jobs = jobs.filter(created_at__gte=today - timezone.timedelta(days=30))
     # Tri
    sort_by = request.GET.get('sort')
    if sort_by == 'date_desc':
        jobs = jobs.order_by('-created_at')
    elif sort_by == 'date_asc':
        jobs = jobs.order_by('created_at')
    elif sort_by == 'salary_desc':
        jobs = jobs.order_by('-salary_range')
    elif sort_by == 'salary_asc':
        jobs = jobs.order_by('salary_range')
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    # Récupérer les locations uniques pour le filtre
    locations = JobOffer.objects.values_list('location', flat=True).distinct()
    
    context = {
        'jobs': jobs,
        'query': query,
        'location': location,
        'min_salary': min_salary,
        'max_salary': max_salary,
        'date_filter': date_filter,
        'sort_by': sort_by,
        'locations': locations,
    }
    
    return render(request, 'jobs/job_list.html', context)
    