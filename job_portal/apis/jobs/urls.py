from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r"jobs", views.JobOfferViewSet, basename="api-job")
router.register(
    r"applications", views.JobApplicationViewSet, basename="api-application"
)

urlpatterns = [
    path("", include(router.urls)),
]

# New API endpoints will be accessible via:
# /jobs/api/jobs/ - List and create job offers
# /jobs/api/jobs/{id}/ - Detail, update, and delete a job offer
# /jobs/api/jobs/my_published_jobs/ - List of offers published by the user
# /jobs/api/jobs/{id}/apply/ - Apply for a job
# /jobs/api/applications/ - List and create applications
# /jobs/api/applications/{id}/ - Detail of an application
# /jobs/api/applications/{id}/cancel/ - Cancel an application
