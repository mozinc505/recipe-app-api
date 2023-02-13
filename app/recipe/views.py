"""
Views for the recipes APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""

    """
    And we're saying APIs, plural, because the view is actually going to generate multiple different endpoints.
    So it's going to have our list endpoint and our ID endpoint or the specific detail endpoint.
    And then it's also going to have the ability to perform multiple different methods for performing different
    actions on the recipes.
    """

    #Konfiguriramo naš viewset

    serializer_class = serializers.RecipeSerializer


    #The queryset represents the objects that were available for this view.
    #S tem poveš s katerimi objekti bodo teli APIji delali (ker je ModelViewset pričakuje modele)
    queryset = Recipe.objects.all()

    #In order to use any of the endpoints that provided by this feature, you need to use token authentication
    authentication_classes = [TokenAuthentication]

    #And you need to be authenticated.
    permission_classes = [IsAuthenticated]

    """
    So now what we're going to do is override the get query set method that's provided by our mode of user.
    If we just implemented this view as it is, it would allow us to manage all of the different recipes
    in the system.
    But we want to make sure that those recipes are filtered down to the authenticated user.
    And the way that we do that is we override the get query method.
    """

    #To je metoda, ki jo framework kliče, ko želimo pobrati podatke iz queryseta.
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')