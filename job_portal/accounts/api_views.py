from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import CustomUser
from .serializers import UserSerializer, RegisterSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def signup(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'status': 'success',
                'message': 'Inscription réussie',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_ban(self, request, pk=None):
        user = self.get_object()
        
        if user.is_staff or user.is_superuser:
            return Response({
                'status': 'error',
                'message': 'Impossible de bannir un administrateur'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if user.is_banned:
            user.unban_user()
            message = f"L'utilisateur {user.username} a été débanni"
        else:
            user.ban_user()
            message = f"L'utilisateur {user.username} a été banni"
        
        return Response({
            'status': 'success',
            'message': message
        })