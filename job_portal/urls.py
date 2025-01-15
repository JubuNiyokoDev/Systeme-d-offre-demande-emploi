from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
schema_view = get_schema_view(
    openapi.Info(
        title="Job Portal API",
        default_version='v1',
        description="API pour le système d'offre-demande emploi",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='jobs:available_jobs'), name='home'),
    path('accounts/', include('apps.accounts.urls')),
    path('jobs/', include('apps.jobs.urls', namespace='jobs')),
    
    path('api/', include([
        path('auth/', include('rest_framework.urls')), 
        path('jobs/', include('apis.jobs.urls')),  
        path('accounts/', include('apis.accounts.urls')), 
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
       path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
]

