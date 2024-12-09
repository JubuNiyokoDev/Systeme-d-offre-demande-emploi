from django import forms
from .models import JobOffer, JobApplication

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
        
class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes internes sur le candidat...'
            }),
        }
        labels = {
            'status': 'Statut de la candidature',
            'notes': 'Notes internes'
        }
        
class JobSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Rechercher',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher un poste, une entreprise...'
        })
    )
    
    location = forms.CharField(
        required=False,
        label='Lieu',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ville, région...'
        })
    )
    
    min_salary = forms.IntegerField(
        required=False,
        label='Salaire minimum',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Salaire minimum'
        })
    )
    
    max_salary = forms.IntegerField(
        required=False,
        label='Salaire maximum',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Salaire maximum'
        })
    )
    DATE_CHOICES = [
        ('', 'Toutes les dates'),
        ('today', "Aujourd'hui"),
        ('week', 'Cette semaine'),
        ('month', 'Ce mois-ci'),
    ]
    
    date_filter = forms.ChoiceField(
        choices=DATE_CHOICES,
        required=False,
        label='Date de publication',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    SORT_CHOICES = [
        ('date_desc', 'Plus récent'),
        ('date_asc', 'Plus ancien'),
        ('salary_desc', 'Salaire décroissant'),
        ('salary_asc', 'Salaire croissant'),
    ]
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        label='Trier par',
        widget=forms.Select(attrs={'class': 'form-select'})
    )