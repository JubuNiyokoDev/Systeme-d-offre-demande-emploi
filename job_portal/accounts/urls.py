from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views
from django.contrib.auth import views as auth_views

# Configuration du routeur pour l'API
router = DefaultRouter()
router.register(r'users', api_views.UserViewSet)

app_name = 'accounts'


urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),  # URLs d'authentification DRF
    
    # URLs d'authentification et de gestion de compte
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # URLs de gestion des utilisateurs
    path('users/', views.user_list, name='user_list'),
    path('users/toggle-ban/<int:user_id>/', views.toggle_ban_user, name='toggle_ban'),
    
    # URLs de profil
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # URLs de gestion du mot de passe
    path('password/change/', views.password_change, name='password_change'),
    path('password/change/done/', views.password_change_done, name='password_change_done'),
    
    # URLs de réinitialisation du mot de passe
    path('password/reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/accounts/password/reset/done/'
    ), name='password_reset'),
    
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/password/reset/complete/'
    ), name='password_reset_confirm'),
    
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]

# Les URLs de l'API seront accessibles via :
# /accounts/api/users/ - Liste et création d'utilisateurs
# /accounts/api/users/{id}/ - Détail, modification et suppression d'un utilisateur
# /accounts/api/users/signup/ - Inscription d'un nouvel utilisateur
# /accounts/api/users/{id}/toggle-ban/ - Bannir/débannir un utilisateur