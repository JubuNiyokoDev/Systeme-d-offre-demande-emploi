from django.urls import path, include
from . import views

app_name = 'jobs'

urlpatterns = [
    # API URLs
    path('api/', include('jobs.api_urls')),
    
    # URLs Web existantes
    path('', views.available_jobs, name='available_jobs'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('create/', views.job_create, name='job_create'),
    path('<int:job_id>/edit/', views.job_edit, name='job_edit'),
    path('<int:job_id>/apply/', views.apply_to_job, name='job_apply'),
    path('<int:job_id>/applications/', views.job_applications, name='job_applications'),
    path('<int:job_id>/delete/', views.job_delete, name='job_delete'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('applications/', views.manage_applications, name='manage_applications'),
    path('applications/<int:job_id>/', views.manage_applications, name='manage_applications_by_job'),
    path('application/<int:application_id>/update/', views.update_application_status, name='update_application_status'),
]
# Les nouveaux endpoints API seront accessibles via:
# /jobs/api/jobs/ - Liste et création d'offres
# /jobs/api/jobs/{id}/ - Détail, modification et suppression d'une offre
# /jobs/api/jobs/my_published_jobs/ - Liste des offres publiées par l'utilisateur
# /jobs/api/jobs/{id}/apply/ - Postuler à une offre
# /jobs/api/applications/ - Liste et création de candidatures
# /jobs/api/applications/{id}/ - Détail d'une candidature
# /jobs/api/applications/{id}/cancel/ - Annuler une candidature