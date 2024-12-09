from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from ..models import JobOffer, JobApplication
from accounts.models import CustomUser

class JobOfferAPITests(APITestCase):
    def setUp(self):
        # Créer un utilisateur de test
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            is_recruiter=True
        )
        self.client.force_authenticate(user=self.user)

    def test_create_job(self):
        """Test la création d'une offre d'emploi"""
        url = reverse('api-job-list')
        data = {
            'title': 'Développeur Python',
            'description': 'Description du poste',
            'company': 'Test Company',
            'location': 'Paris',
            'salary_range': 50000,
            'status': 'active',  # Ajout du statut
            'expires_at': (timezone.now() + timedelta(days=30)).isoformat(),  # Ajout de la date d'expiration
        }
        
        response = self.client.post(url, data, format='json')
        
        print("Response data:", response.data)  # Pour déboguer
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JobOffer.objects.count(), 1)
        
        # Vérifier les détails de l'offre créée
        job = JobOffer.objects.first()
        self.assertEqual(job.title, 'Développeur Python')
        self.assertEqual(job.company, 'Test Company')
        self.assertEqual(job.publisher, self.user)