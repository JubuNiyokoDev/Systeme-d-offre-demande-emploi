from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets


class JobOfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des offres d'emploi.
    """

    @swagger_auto_schema(
        operation_description="Liste toutes les offres d'emploi",
        manual_parameters=[
            openapi.Parameter(
                "q",
                openapi.IN_QUERY,
                description="Recherche par mot-clé",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "location",
                openapi.IN_QUERY,
                description="Filtrer par lieu",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Créer une nouvelle offre d'emploi")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
