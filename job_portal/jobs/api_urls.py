from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobOfferViewSet, JobApplicationViewSet

app_name = 'jobs_api'

router = DefaultRouter()
router.register(r'offers', JobOfferViewSet)
router.register(r'applications', JobApplicationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]