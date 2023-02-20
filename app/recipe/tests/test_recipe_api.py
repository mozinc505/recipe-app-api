"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe details URL."""
    return reverse('recipe:recipe-detail',args=[recipe_id])


#region HELPER FUNCTIONS

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

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)

#endregion


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

        self.user = create_user(email='user@example.com', password='testpass123')

        """
        #Create a user
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        """

        #Authenticate a client with this user
        self.client.force_authenticate(self.user)

#region TEST: Recipe List
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
        """
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        """
        other_user = create_user(email="other@example.com", password="password123")

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
#endregion

#region TEST: Recipe Details
    def test_get_recipe_detail(self):
        """Test get recipe detail."""

        #Create a sample recipe and assign it to the authenticated user
        recipe = create_recipe(user=self.user)

        #Create a detail URL using the ID of that recipe
        url = detail_url(recipe.id)

        #Call the URL
        res = self.client.get(url)

        #Pass in the recipe that we created, to the serializer
        serializer = RecipeDetailSerializer(recipe)

        #Check the result: Compare if what we got from URL is the same as what we created
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""

        #OPOMBA: Pri tej metodi ne uporabimo helper metode za kreiranje recepta (zapisa), ker je glavni namen tega testa,
        #da preverimo samo kreiranje zapisa (recepta) preko API-ja (URL-ja). Kreiramo podatke, jih pošljemo API-ju in preverimo
        #ali je bil zapis pravilno narejen v podatkovni bazi.

        #Pripravimo podatke v dictionary-ju
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload) # /api/recipes/recipe

        #Preverimo ali je zahteva uspela
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        #Poberemo zdaj ta podatek iz baze in naredimo "check"
        recipe = Recipe.objects.get(id=res.data['id'])

        #Se zavrtimo čez payload --> k=key, v=value
        for k, v in payload.items():
            #getatt je python funkcija --> vrne atribut s tem imenom (k), ki se nahaja v tem objektu. Torej vrednost artibuta s tem imenom.
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
#endregion

    def test_partial_update(self):
        """Test partial update of a recipe. Updating just a part of object."""

        #Testiramo posodobitev samo določenih podatkov in da ostali niso spremenjeni.

        #Naredimo insert
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user = self.user,
            title = 'Sample recipe title',
            link = original_link,
        )

        #Naredimo update
        payload = {'title': 'New recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        #Naredimo test (check)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db() #Django ne refresha podatke avtomatično, ko jih update-aš.
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)


    def test_full_update(self):
        """"Test full update of recipe."""

        #Naredimo in shranimo
        recipe = create_recipe(
            user = self.user,
            title = "Sample recipe title",
            link = "https://example.com/recipe.pdf",
            description = "Sample recipe description",
        )

        #Naredimo update
        payload = {
            "title": "New recipe title",
            "link": "https://example.com/new-recipe.pdf",
            "description": "New recipe description",
            "time_minutes": 10,
            "price": Decimal("2.50"),
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_return_error(self):
        """Test changing the recipe user returns error."""
        new_user = create_user(email="user2@example.com", password="test123")
        recipe = create_recipe(user=self.user)

        payload = {"user": new_user}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe succesfull."""

        #Naredimo in shranimo
        recipe = create_recipe(user=self.user)

        #Zbrišemo
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT) #Standarden odgovor za uspešno brisanje
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists()) #Kontrola, da zapis res ne obstaja več v bazi


    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url) #Brisanje (request) se izvede z avtenticiranim uporabnikom (self.user) --> recept pa se nanaša na new_user

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())


    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json') #Explicitno zapišemo, da hočemo json (ker uporabljamo vgnezdene podatke)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        #Poberemo podatke tega user-ja iz baze
        recipes = Recipe.objects.filter(user=self.user)


        #Poberemo prvi recept
        self.assertEqual(recipes.count(), 1) #Kontrola, da res obstaja
        recipe = recipes[0]

        #Kontrola: Mora imeti 2 tag-a
        self.assertEqual(recipe.tags.count(), 2)

        #Kontrola: da je vsak tag iz payload podatkov res v bazi (za tega uporabnika)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""

        #Da uporabnik ne doda večkrat isti tag

        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        #Poberemo podatke iz baze za tega user-ja
        recipes = Recipe.objects.filter(user=self.user)

        #Iz seznama vzamemo prvi zapis
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)

        self.assertIn(tag_indian, recipe.tags.all())

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating tag when updating a recipe."""

        """
        So in this particular test, we're going to check that if we update a recipe, but we provide a different
        time that doesn't exist, then we're going to create that tag in the system.
        """

        #Naredimo nov testni recept
        recipe = create_recipe(user=self.user)

        #Naredimo seznam podatkov za tag
        payload = {"tags": [{"name": "Lunch"}]}

        #Preko API-ja dodamo ta tag na recept
        url = detail_url(recipe.id) #URL od recepta
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        #Poberemo ta isti podatek iz baze
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, recipe.tags.all()) #OPOMBA: Ne potrebujemo refresh_from_db --> pri ManyToMany poljih (ker naredi nov query)


    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]} #OPOMBA: Zamenjali bomo celoten seznam tag-ov za ta recept (ker gre za array)
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tags."""
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []} #prazen seznam
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients."""
        payload = {
            "title": "Cauliflower Tacos",
            "time_minutes": 60,
            "price": Decimal("4.30"),
            "ingredients": [{"name": "Cauliflower"}, {"name": "Salt"}],
        }
        res = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name = ingredient["name"],
                user = self.user,
            ).exists
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self):
        """Test creating a new recipe with existing ingredient."""
        #ingredient = Ingredient.objects.create(user = self.user, name = "Lemon")
        ingredient = Ingredient.objects.create(user=self.user, name='Lemon')
        payload = {
            "title": "Vietnamese Soup",
            "time_minutes": 25,
            "price": "2.55",
            "ingredients": [{"name": "Lemon"}, {"name": "Fish Sauce"}],
        }
        res = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(),1)

        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(),2)
        self.assertIn(ingredient, recipe.ingredients.all())

        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name = ingredient["name"],
                user = self.user,
            ).exists
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient when updating a recipe."""
        recipe = create_recipe(user = self.user)

        payload = {"ingredients": [{"name": "Limes"}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name="Limes") #Poberemo zapis iz baze
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient when updating a recipe."""
        ingredient1 = Ingredient.objects.create(user=self.user, name="Pepper")
        recipe = create_recipe(user = self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name="Chili")
        payload = {"ingredients": [{"name": "Chili"}]}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())


    def test_clear_recipe_ingredients(self):
        """Test clearing a recipe ingredients."""
        ingredient = Ingredient.objects.create(user=self.user, name="Garlic")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {"ingredients": []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)