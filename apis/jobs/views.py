from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.jobs.models import JobOffer, JobApplication
from .serializers import JobOfferSerializer, JobApplicationSerializer
from django.utils import timezone

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q

from apps.jobs.models import JobOffer, JobApplication
from .serializers import JobOfferSerializer, JobApplicationSerializer

class JobOfferViewSet(viewsets.ModelViewSet):
    serializer_class = JobOfferSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'company', 'location']
    search_fields = ['title', 'description', 'company']
    ordering_fields = ['created_at', 'expires_at']

    def get_queryset(self):
        queryset = JobOffer.objects.all()
        
        # Filtrage par mot-clé
        query = self.request.query_params.get('q', '')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(company__icontains=query) |
                Q(description__icontains=query)
            )
        
        # Filtrage par localisation
        location = self.request.query_params.get('location', '')
        if location:
            queryset = queryset.filter(location__iexact=location)
        
        # Filtrage par salaire
        min_salary = self.request.query_params.get('min_salary')
        max_salary = self.request.query_params.get('max_salary')
        if min_salary and min_salary.isdigit():
            queryset = queryset.filter(salary_range__gte=int(min_salary))
        if max_salary and max_salary.isdigit():
            queryset = queryset.filter(salary_range__lte=int(max_salary))
        
        # Filtrage par date
        date_filter = self.request.query_params.get('date_filter')
        if date_filter:
            today = timezone.now()
            if date_filter == 'today':
                queryset = queryset.filter(created_at__date=today.date())
            elif date_filter == 'week':
                queryset = queryset.filter(
                    created_at__gte=today - timezone.timedelta(days=7)
                )
            elif date_filter == 'month':
                queryset = queryset.filter(
                    created_at__gte=today - timezone.timedelta(days=30)
                )
        
        # Filtrage selon l'action
        if self.action == 'my_published_jobs':
            return queryset.filter(publisher=self.request.user)
        if self.action == 'available_jobs':
            return queryset.filter(
                status='active',
                expires_at__gt=timezone.now()
            ).exclude(publisher=self.request.user)
        
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        if not self.request.user.is_recruiter:
            raise PermissionDenied("Seuls les recruteurs peuvent créer des offres")
        serializer.save(publisher=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.publisher != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Vous n'êtes pas autorisé à modifier cette offre")
        serializer.save()

    @action(detail=False)
    def my_published_jobs(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False)
    def available_jobs(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        job = self.get_object()
        if request.user.is_recruiter:
            raise PermissionDenied("Les recruteurs ne peuvent pas postuler")
        if job.publisher == request.user:
            raise PermissionDenied("Vous ne pouvez pas postuler à votre propre offre")
        if job.is_expired:
            raise PermissionDenied("Cette offre a expiré")
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            raise PermissionDenied("Vous avez déjà postulé à cette offre")
        
        application = JobApplication.objects.create(
            job=job,
            applicant=request.user
        )
        
        return Response({
            'status': 'success',
            'message': 'Candidature envoyée avec succès'
        }, status=status.HTTP_201_CREATED)
class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = JobApplication.objects.all()
        
        # Filtrage par statut
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        if self.request.user.is_recruiter:
            return queryset.filter(job__publisher=self.request.user)
        return queryset.filter(applicant=self.request.user)

    def perform_create(self, serializer):
        job = serializer.validated_data['job']
        
        # Vérifications
        if self.request.user.is_recruiter:
            raise PermissionDenied("Les recruteurs ne peuvent pas postuler")
        if job.publisher == self.request.user:
            raise PermissionDenied("Vous ne pouvez pas postuler à votre propre offre")
        if job.is_expired:
            raise PermissionDenied("Cette offre a expiré")
        if JobApplication.objects.filter(job=job, applicant=self.request.user).exists():
            raise PermissionDenied("Vous avez déjà postulé à cette offre")
        
        serializer.save(applicant=self.request.user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        application = self.get_object()
        
        # Vérifier que l'utilisateur est le recruteur de l'offre
        if application.job.publisher != request.user:
            raise PermissionDenied(
                "Seul le recruteur peut modifier le statut de la candidature"
            )
        
        new_status = request.data.get('status')
        if new_status not in dict(JobApplication.STATUS_CHOICES):
            return Response(
                {"error": "Statut invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application.status = new_status
        application.save()
        
        return Response({
            "status": "success",
            "message": "Statut mis à jour avec succès"
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        application = self.get_object()
        
        # Vérifier que l'utilisateur est le candidat
        if application.applicant != request.user:
            raise PermissionDenied(
                "Seul le candidat peut annuler sa candidature"
            )
        
        application.status = 'cancelled'
        application.save()
        
        return Response({
            "status": "success",
            "message": "Candidature annulée avec succès"
        })