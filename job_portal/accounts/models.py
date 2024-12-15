from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        verbose_name="Numéro de téléphone",
        help_text="Format: +257 61895940"
    )
    is_banned = models.BooleanField(
        default=False,
        verbose_name="Utilisateur banni",
        help_text="Indique si l'utilisateur est banni du système"
    )
    is_admin = models.BooleanField(default=False,null=True,blank=True)
    is_superuser = models.BooleanField(default=False,null=True,blank=True)


    def __str__(self):
        return f"{self.username} ({self.email})"

    def ban_user(self):
        self.is_banned = True
        self.save()

    def unban_user(self):
        self.is_banned = False
        self.save()
    is_banned = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_recruiter = models.BooleanField(default=False)

    def __str__(self):
        return self.email