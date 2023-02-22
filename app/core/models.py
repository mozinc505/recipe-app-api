from django.db import models # noqa
"""
Database models.
"""

import uuid # will be used to generate UID
import os # we need for file path management

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


# Funkcija, ki se bo uporabljala za generiranje poti do slike, ki jo upload-amo
# So this is the function that is going to be used to generate the path to the image that we upload.
# PARAM:
# instance = is the instance of the object the image is being uploaded to
# filename = the name of the original file that's been uploaded.
def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""

    # Odstranimo končnico (stripping off the extension)
    ext = os.path.splitext(filename)[1]

    # Naredimo svoje ime file-a (pripnemo pa originalno končnico)
    filename = f'{uuid.uuid4()}{ext}'

    # Kreiramo pot (s funkcijo - join)
    # Na ta način je pot narejena v pravilni obliki (glede na dovoljene znake)
    return os.path.join("uploads", "recipe", filename)


# Create your models here.

class UserManager(BaseUserManager):
    """Manager for users"""


    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return user"""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields) #Manager je povezan z modelom in na ta način dostopamo do modela s katerim je povezan
        user.set_password(password)
        user.save(using=self._db) #Podpora za več baz (zato pošljem _db kot parameter)

        return user

    def create_superuser(self, email, password):
        """Create and return new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager() # Na ta način povežemo User Managerja z modelom

    USERNAME_FIELD = 'email'

class Recipe(models.Model):
    """Recipe objects."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, #relacija na User model --> ker uporabljamo custom User model naredimo referenco rajši preko settingsov (tam smo definirali kateru User model uporabljamo)
        on_delete=models.CASCADE,
    )

    #TextField vs CharField
    #Textfiels je za daljši tekst in podpira večrstično vsebino
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True) #blank=True pomeni, da je polje neobvezno
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True) #web link do spletne strani recepta
    tags = models.ManyToManyField("Tag")
    ingredients = models.ManyToManyField("Ingredient")
    image = models.ImageField(null=True, upload_to=recipe_image_file_path) # referenca na funkcijo (nismo poklicali/zagnali funkcijo)
    #String representation of the object
    #To vpliva tudi kako se prikazuje v Django-Admin (na spletni strani)
    def __str__(self):
        return self.title

class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )

    #String representation of the object
    def __str__(self):
        return self.name

class Ingredient(models.Model):
    """Ingredient for recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
