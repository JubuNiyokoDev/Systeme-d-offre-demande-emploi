from django.db import models
from django.conf import settings
from django.utils import timezone

class JobOffer(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('closed', 'Closed'),
    )
    title = models.CharField(max_length=200, verbose_name="Titre du poste")
    salary_range = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Fourchette de salaire",
        help_text="Example: 45000-55000"
    )
    
    
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"

    def save(self, *args, **kwargs):
        if self.expires_at < timezone.now():
            self.status = 'expired'
        super().save(*args, **kwargs)

    title = models.CharField(max_length=200)
    description = models.TextField()
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    publisher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='published_jobs')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    salary_range = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        return self.expires_at < timezone.now()

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('reviewing', 'En cours d\'examen'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
    )

    job = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField()
    notes = models.TextField(blank=True, help_text="Notes internes sur le candidat")  # Nouveau champ

    class Meta:
        unique_together = ('job', 'applicant')