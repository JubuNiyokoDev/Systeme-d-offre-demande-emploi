from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Existing web URLs
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

