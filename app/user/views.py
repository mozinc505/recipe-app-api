"""
Views for the user API.
"""
#from django.shortcuts import render
# Create your views here.

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)

#OPOMBA: CreateAPIView handles a HTTP POST request, that is designed for creating objects
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    #S tem povemo django-u kateri serializer želimo uporabiti.
    #Vedel pa bo tudi v katerem modelu želimo narediti objekt, ker ima serializer v metapodatkih določeno kateri modul naj uporablja
    serializer_class = UserSerializer


#Uporabimo obstoječi view, ki ga zagotavlja že Django za kreiranje vseh Token-ov.
#Samo popravimo kar rabimo (override)
class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer

    #What this does it uses the default render of classes for this obtain or token view.
    #By default, if we want to include this, we wouldn't get the browseable API that's used for Django REST framework.
    #It wouldn't show a nice user interface for that.
    #Django REST Framework supports generating human-friendly HTML output for each resource when the HTML format is requested.
    #IN ORDER to make to that is enabled on this new view, we are adding it manually inside the view.
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


#Naredimo klas na podlagi Django classa - RetrieveUpdateAPIView - ki se uporablja za vračanje in posodabljanje objektov v podatkovni bazi.
#Retrieving --> HTTP.GET, Updating --> HTTP.PATCH and HTTP.PUT
class  ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer #Nastavimo serializer

    #Nastavimo klase za avtentikacijo.
    #Avtentikacija v Django rest frameworku je razdeljena na dve stvari:
    #   - Avtentikacijo --> kako veš, da je nekdo res ta za katerega se izdaja (za ta namen v tem primeru uporabljamo Token Authentication)
    #   - Permission --> da vemo kdo uporabnik res je in kaj lahko pocne v tem sistemu
    #       --> v tem primeru želimo, da je uporabnik, ki uporablja ta API res avtenticiran (.IsAuthenticated)
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    #Override-amo get_object metodo
    #Ta metoda vrne objekte pri HTTP.GET klicu oz. katerikoli zahtevi, ki je narejena do tega API-ja
    def get_object(self):
        """Retrieve and return the authenticated user."""
        #Vrnemo samo uporabnika, ki je vezan na to zahtevo.

        #The way that authentication system works is that when a user is authenticated,
        #the user object that is being authenticated gets assigned to the request object
        #that's available in the view.

        #So, when we make a HTTP.GET request to this endpoint, it's going to call get objects to get the user,
        #it's going to retrieve the user that was authenticated and then it's going to run it through our serializer
        #that we defined, before returning the result to the API.
        return self.request.user