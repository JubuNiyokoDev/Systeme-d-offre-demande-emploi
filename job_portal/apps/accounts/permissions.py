from rest_framework import permissions

class IsAdminOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Vérifiez si l'utilisateur est authentifié
        if not request.user.is_authenticated:
            return False
        
        # Vérifiez les permissions
        return request.user.is_staff or request.user.is_admin or request.user.is_superuser or obj == request.user