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
from .serializers import JobOfferSerializer, JobApplicationSerializer
from .forms import JobOfferForm, JobApplicationForm
from accounts.models import CustomUser

# API ViewSets
class JobOfferViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'company', 'location']
    search_fields = ['title', 'description', 'company']
    ordering_fields = ['created_at', 'expires_at']

    def perform_create(self, serializer):
        serializer.save(publisher=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.publisher != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Vous n'êtes pas autorisé à modifier cette offre")
        serializer.save()

    def get_queryset(self):
        queryset = JobOffer.objects.all()
        if self.action == 'my_published_jobs':
            return queryset.filter(publisher=self.request.user)
        if self.action == 'available_jobs':
            return queryset.filter(
                status='active',
                expires_at__gt=timezone.now()
            ).exclude(publisher=self.request.user)
        return queryset

    @action(detail=False, methods=['get'])
    def my_published_jobs(self, request):
        jobs = self.get_queryset()
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available_jobs(self, request):
        jobs = self.get_queryset()
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        job = serializer.validated_data['job']
        # Vérifications supplémentaires
        if job.publisher == self.request.user:
            raise PermissionDenied("Vous ne pouvez pas postuler à votre propre offre")
        if job.is_expired:
            raise PermissionDenied("Cette offre a expiré")
        if JobApplication.objects.filter(job=job, applicant=self.request.user).exists():
            raise PermissionDenied("Vous avez déjà postulé à cette offre")
        
        serializer.save(applicant=self.request.user)

    def get_queryset(self):
        if self.action == 'my_applications':
            return JobApplication.objects.filter(applicant=self.request.user)
        return JobApplication.objects.filter(job__publisher=self.request.user)

    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        applications = self.get_queryset()
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)

# Vue pour les offres d'emploi
@login_required
def available_jobs(request):
    query = request.GET.get('q', '')
    jobs = JobOffer.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        status='active',
        expires_at__gt=timezone.now()
    ).exclude(publisher=request.user).order_by('-created_at')
    return render(request, 'jobs/available_jobs.html', {'jobs': jobs, 'query': query})

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
    job = get_object_or_404(JobOffer, id=job_id, publisher=request.user)
    if request.method == 'POST':
        form = JobOfferForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "L'offre d'emploi a été mise à jour avec succès.")
            return redirect('jobs:my_jobs')
    else:
        form = JobOfferForm(instance=job)
    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Modifier l\'offre'})

# Vues pour les candidatures
@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(JobOffer, id=job_id)
    
    if job.publisher == request.user:
        messages.error(request, "Vous ne pouvez pas postuler à votre propre offre.")
        return redirect('jobs:available_jobs')
    
    if job.is_expired:
        messages.error(request, "Cette offre a expiré.")
        return redirect('jobs:available_jobs')
    
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.error(request, "Vous avez déjà postulé à cette offre.")
        return redirect('jobs:available_jobs')
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Votre candidature a été envoyée avec succès!")
            return redirect('jobs:my_applications')
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs/apply.html', {'form': form, 'job': job})

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
def job_edit(request, job_id):
    job = get_object_or_404(JobOffer, id=job_id)
    
    # Vérifier les permissions
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