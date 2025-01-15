from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import JobOffer
from apps.accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Crée des données de test pour le système d\'offres d\'emploi'

    def handle(self, *args, **kwargs):
        try:
            # Créer un utilisateur test
            user, created = CustomUser.objects.get_or_create(
                username='testuser',
                defaults={
                    'email': 'test@example.com',
                    'is_staff': True
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Utilisateur test créé: {user.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'Utilisateur test existe déjà: {user.username}'))

            # Créer quelques offres d'emploi
            job_titles = [
                'Développeur Python Senior',
                'Développeur Full Stack',
                'Data Scientist',
                'DevOps Engineer',
                'Product Manager'
            ]

            companies = ['Tech Corp', 'Digital Solutions', 'AI Labs', 'Cloud Systems', 'Innovation Inc']
            locations = ['Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Toulouse']

            for i in range(5):
                job, created = JobOffer.objects.get_or_create(
                    title=job_titles[i],
                    defaults={
                        'description': f'Nous recherchons un {job_titles[i]} expérimenté pour rejoindre notre équipe.',
                        'company': companies[i],
                        'location': locations[i],
                        'publisher': user,
                        'expires_at': timezone.now() + timedelta(days=30),
                        'salary_range': f'{40000 + i*10000}-{50000 + i*10000}'
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Offre créée: {job.title}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Offre existe déjà: {job.title}'))

            self.stdout.write(self.style.SUCCESS('Toutes les données de test ont été créées avec succès!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de la création des données: {str(e)}'))