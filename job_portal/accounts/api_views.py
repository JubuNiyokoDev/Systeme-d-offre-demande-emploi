from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import CustomUser
from .serializers import UserSerializer, RegisterSerializer
from .permissions import IsAdminOrSelf
from django.contrib.auth import authenticate


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by('id') 
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrSelf()]
        return [AllowAny()] 

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
        user = self.get_object()  # Récupère l'utilisateur par ID
        
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
    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        if not request.user.is_authenticated:
            return Response({
                'status': 'error',
                'message': 'Vous devez être connecté pour mettre à jour votre profil.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user  # Récupère l'utilisateur authentifié
        username = request.data.get('username')

        # Vérifiez si le nom d'utilisateur est déjà pris par un autre utilisateur
        if username and CustomUser.objects.exclude(id=user.id).filter(username=username).exists():
            return Response({
                'status': 'error',
                'message': 'Un utilisateur avec ce nom d’utilisateur existe déjà.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
            

        serializer = UserSerializer(user, data=request.data, partial=True)  # Utilise partial=True pour permettre des mises à jour partielles

        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Profil mis à jour avec succès',
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'status': 'success',
            'message': 'Compte supprimé avec succès.'
        }, status=status.HTTP_204_NO_CONTENT)