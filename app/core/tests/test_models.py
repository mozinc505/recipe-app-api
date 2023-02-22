"""
Tests for models.
"""

from unittest.mock import patch #This is the tool we use to mock things (replace behaviour for the purpose of testing)
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model #Je dobro da uporabiš to metodo, da dobiš referenco do svojega custom user modela

from core import models

def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normilized for new users"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    #----------
    #TESTS FOR RECIPE
    #----------
    def test_create_recipe(self):
        """Test creating a reipe is successul."""

        #Create a user so we can assign a recipe to that user (in our test)
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user = user, #user, ki so smo v zgornjem koraku kreirali
            title = 'Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'), #String to decimal
            description='Sample recipe description',
        )

        self.assertEqual(str(recipe), recipe.title)


    #----------
    #TESTS FOR TAGs
    #----------
    def test_create_tag(self):
        """Test creating a tag is successul."""

        #Create a user so we can assign it to the tag (in our test)
        user = create_user()

        tag = models.Tag.objects.create(user=user, name="Tag1")

        self.assertEqual(str(tag), tag.name)


    #----------
    #TESTS FOR INGREDIENTS
    #----------
    def test_create_ingridient(self):
        """Test creating an ingredient is succesfull"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user = user,
            name = "Ingredient1",
        )

        self.assertEqual(str(ingredient), ingredient.name)


    #Z @patch ukazom samo posnemamo funkcionalnoste te metode
    #Za potrebe testiranja nočemo, da uuid metoda naredi dolg unique string (ker je težje debugairat)
    @patch("core.models.uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""

        """
        And this is going to be the unit test for the functionality or the function that we're going to create
        for creating the path to the file on the system.
        """

        #Vsak upload-an file bo dobil uuid ime - da bodo imena enolična
        uuid = "test-uuid" # S tem posnemamo obnašanje funkcije
        mock_uuid.return_value = uuid

        # A function that generates the path to the image that is being uploaded.
        file_path = models.recipe_image_file_path(None, "example.jpg")

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')