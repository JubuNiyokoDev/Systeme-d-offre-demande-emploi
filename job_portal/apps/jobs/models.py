from django.db import models
from job_portal.settings import base
from django.utils import timezone


class JobStatus(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nom du statut")
    description = models.TextField(blank=True, verbose_name="Description du statut")

    class Meta:
        verbose_name = "Statut de l'offre d'emploi"
        verbose_name_plural = "Statuts des offres d'emploi"

    def __str__(self):
        return self.name


class ApplicationStatus(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nom du statut")
    description = models.TextField(blank=True, verbose_name="Description du statut")

    class Meta:
        verbose_name = "Statut de la candidature"
        verbose_name_plural = "Statuts des candidatures"

    def __str__(self):
        return self.name


class JobOffer(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre du poste")
    description = models.TextField(verbose_name="Description")
    company = models.CharField(max_length=100, verbose_name="Entreprise")
    location = models.CharField(max_length=100, verbose_name="Lieu")
    publisher = models.ForeignKey(
        base.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="published_jobs",
        verbose_name="Publié par",
    )
    status = models.ForeignKey(
        JobStatus, on_delete=models.SET_NULL, null=True, verbose_name="Statut"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    expires_at = models.DateTimeField(verbose_name="Date d'expiration")
    salary_range = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Fourchette de salaire",
        help_text="Exemple : 45000-55000",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"

    def save(self, *args, **kwargs):
        if self.expires_at < timezone.now():
            expired_status, _ = JobStatus.objects.get_or_create(
                name="Expired",
                defaults={"description": "Statut automatique pour les offres expirées"},
            )
            self.status = expired_status
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        return self.expires_at < timezone.now()


class JobApplication(models.Model):
    job = models.ForeignKey(
        JobOffer,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Offre d'emploi",
    )
    applicant = models.ForeignKey(
        base.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications",
        verbose_name="Candidat",
    )
    status = models.ForeignKey(
        ApplicationStatus, on_delete=models.SET_NULL, null=True, verbose_name="Statut"
    )
    applied_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de candidature"
    )
    cover_letter = models.TextField(verbose_name="Lettre de motivation")
    notes = models.TextField(
        blank=True,
        verbose_name="Notes internes",
        help_text="Notes internes sur le candidat",
    )

    class Meta:
        unique_together = ("job", "applicant")
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"

    def __str__(self):
        return f"Candidature de {self.applicant} pour {self.job.title}"
