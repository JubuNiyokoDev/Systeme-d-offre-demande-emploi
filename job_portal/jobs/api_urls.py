from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views


router = DefaultRouter()
router.register(r'jobs', api_views.JobOfferViewSet, basename='api-job')
router.register(r'applications', api_views.JobApplicationViewSet, basename='api-application')

urlpatterns = [
    path('', include(router.urls)),
]