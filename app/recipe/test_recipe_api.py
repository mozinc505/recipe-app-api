"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


#Create a helpers function for creating Recipe.
#This will be used for creating a test recipe that we can use with our API.
#PARAMETRI:
#   - **params --> je dictionary
def create_recipe(user, **params):
    """Create and return a sample recipe"""

    #Naredimo seznam privzetih podatkov (ker vedno ne potrebujemo vseh in zato v "params" ne bodo vedno vsi posredovani)
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params) #Na podlagi dictionary-ja "params" posodobimo vse enakoimenske podatke v dictionary-ju "default" (če so bil v "params" posredovani kakšni enaki)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

"""
PUBLIC TESTI
"""
class PublicRecipeApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    #TEST: Avtentikacija je nujna, za dostop do tega endpointa (za pobiranje podatkov o receptih)
    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

"""
PRIVATE TESTI
"""
class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        #Create a client
        self.client = APIClient()

        #Create a user
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )

        #Authenticate a client with this user
        self.client.force_authenticate(self.user)


    def test_retrieve_recepies(self):
        """Test retrieving recipes"""

        #Naredimo dva recepta (edini obvezni podatek je user, ostalo pustimo kar default)
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        #Poberemo podatke (jih sortiramo po ID padajoče --> zato ta minus znak)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True) #Serializer lahko sprejme/vrne 1 podatek ali VEČ podatkov

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data) #Data dictionary of the objects passed through th serializer

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""

        #Kontrola, da vedno poberemo podatke samo od danega user-ja (ne pa tudi od ostalih user-jev)
        #Naredimo nekaj receptov za nekega drugage userja in preverimo, da jih ne poberemo pri tem userju.
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        #Naredimo recept za tega drugega uporabnika
        create_recipe(user=other_user)

         #Naredimo recepta še za prvega userja
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        #Poberemo vse recepte za uporabnika (filter na avtenticiranega uporabnika
        recipes = Recipe.objects.filter(user=self.user)

        #Posredujemo podatke, čez serializator
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data) #Data dictionary of the objects passed through th serializer









