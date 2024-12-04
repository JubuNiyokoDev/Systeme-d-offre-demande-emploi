from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='jobs:available_jobs'), name='home'),
    path('accounts/', include('accounts.urls')),
    
    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('api/', include([
        path('jobs/', include('jobs.api_urls')),  
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ])),
]