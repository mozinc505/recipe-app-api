"""
Views for the recipes APIs
"""
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
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

    serializer_class = serializers.RecipeDetailSerializer #Ta serializer nastavimo kot default (teh akcij bo več)


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


    def get_serializer_class(self):
        """Return the serializer class for request."""

        #-----------
        #OPOMBA: Ker želimo, da za seznam vseh receptov uporabimo en serializer, za prikaz "podrobnosti (details)" pa drugega,
        #to naredimo tako, da override-amo metodo, ki jo DFR uporablja zato, da ugotovi kateri serializer uporabljati
        #-----------

        """
        get_serializer_class(self)
        Returns the class that should be used for the serializer. Defaults to returning the serializer_class attribute.
        May be overridden to provide dynamic behavior, such as using different serializers for read and write operations,
        or p#roviding different serializers to different types of users.
        """

        if self.action == 'list':
            #It expects that we return a reference to the class, not the object of the class.
            #Vrnemo referenco na class --> zato ne smemo uporabiti na koncu (), kar naredi nov class (pokliče konstruktor)
            #DFR bo sam naredil objekt.
            return serializers.RecipeSerializer #Obvezno brez ()

        return self.serializer_class

    """
    Naredimo methodo s katero novim zapisov nastavimo pravega user-ja (zaradi relacije).
    Nastavimo na avtenticiranega uporabnika.
    Override-amo django metodo - we override the behavior for when Django REST Framework saves a model in a viewset.
    Pomeni:
    Ko kreiramo nov objekt (Recipe) skozi ta viewset, se bo poklicala ta metoda kot del kreiranja tega objekta (zapisa).
    Podatki so na tem mestu že validirani s strani serializer-ja.
    """
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)


class BaseRecipeAttrViewSet(mixins.DestroyModelMixin, #handles DELETE
                            mixins.UpdateModelMixin, #handles PUT and PATCHES
                            mixins.ListModelMixin, #handles GET
                            #RetrieveModelMixin, #handled GET for 1 record/object (details)
                            viewsets.GenericViewSet): #generic view funcionality
    """Base viewset for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by("-name")

class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the databaase."""

    #We setup some class-variables:
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    #authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated]

    #def get_queryset(self):
    #    """Filter queryset to authenticated user."""
    #    return self.queryset.filter(user=self.request.user).order_by("-name")

    """
    Mixins is just things that you can mix in to a view to add additional functionality.
    Mixin extend or add ONE specific part of the funcionality.

    #OPOMBA: We through some mixin funcionality to GenericViewSet

    A Mixin is a special kind of inheritance in Python to allow classes to share methods between any class.

    Read this as Mixin1 extends GenericViewSet which is then extended by TagViewSet.

    VIR: https://whiztal.io/mixins-in-django-and-django-rest-framework/
    """


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all() #S tem povemo DRF-ju katere modele želimo, da ta viewset obvladuje
    #authentication_classes = [TokenAuthentication] #S tem dodamo podporo za auth - token-e
    #permission_classes = [IsAuthenticated] #Določimo, da je za uporabo tega endpointa potrebno biti avtenticiran

    #def get_queryset(self):
    #    """Filter queryset to authenticated user."""
    #    return self.queryset.filter(user=self.request.user).order_by("-name")