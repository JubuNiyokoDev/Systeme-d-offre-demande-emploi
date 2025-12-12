from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API router configuration
router = DefaultRouter()
router.register(r"users", views.UserViewSet)

urlpatterns = [
    path("", include(router.urls)),  # Include router URLs
    path("sla/", views.sla_status, name="sla_status"),
]


# API URLs will be accessible via:
# /api/accounts/users/ - List and create users
# /api/accounts/users/{id}/ - Detail, update, and delete a user
# /api/accounts/users/signup/ - Sign up a new user
# /api/accounts/users/{id}/toggle-ban/ - Ban/unban a user
