"""
Tests for tags APIs.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")

def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse("recipe:tag-detail", args=[tag_id])

def create_user(email="example.com", password="testpass123"):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests."""

    """
    TIPS:
    When we call a function with parentheses, the function gets execute and returns the result to the callable.
    In another case, when we call a function without parentheses, a function reference is sent to the callable
    rather than executing the function itself.
    """
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)


    def test_retrieve_tags(self):
        """Test retrieveing a list of tags."""

        #Dodamo (insert) nekaj zapisov v bazo
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        #Make a HTTP.GET request to tags url
        res = self.client.get(TAGS_URL)

        #Poberemo podatke še direktno iz baze (da bomo naredili primerjavo)
        tags = Tag.objects.all().order_by("-name")

        #Serializiramo podatke dobljene s query-jem
        #ZAKAJ: Ker so podatki, ki smo jih dobili z HTTP.GET tudi serializirani (da primerjamo podatke v enaki obliki)
        serializer = TagSerializer(tags, many=True) #Posredovali bomo več objektov --> zato many=True

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""

        #Naredimo dodatnega user-ja in naredimo Tag, ki je vezan nanj
        user2 = create_user(email="user2@example.com")
        Tag.objects.create(user=user2, name="Fruity")

        #Naredimo en Tag, ki je vezan na prvega (authenticiranega) uporabnika
        tag = Tag.objects.create(user=self.user, name="Comfort Food")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1) #Preko API-ja mora dobiti samo 1 zapis
        self.assertEqual(res.data[0]["name"], tag.name) #Ime taga, ki smo ga dobili preko API-ja mora biti enak imenu taga, ki smo ga kreirali in shranili v bazo
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name="After Dinner")

        payload = {"name": "Dessert"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name="Breakfast")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())








