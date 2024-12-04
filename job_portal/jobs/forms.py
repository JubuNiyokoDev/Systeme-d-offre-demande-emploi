from django import forms
from .models import JobOffer, JobApplication

from django import forms
from .models import JobOffer

class JobOfferForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        fields = ['title', 'description', 'company', 'location', 'salary_range', 'expires_at', 'status']
        widgets = {
            'expires_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={'rows': 4, 'class': 'form-control'}
            ),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Titre du poste',
            'description': 'Description',
            'company': 'Entreprise',
            'location': 'Lieu',
            'salary_range': 'Fourchette de salaire',
            'expires_at': "Date d'expiration",
            'status': 'Statut',
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Écrivez votre lettre de motivation ici...'
            })
        }
        labels = {
            'cover_letter': 'Lettre de motivation'
        }