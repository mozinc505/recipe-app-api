"""
URL mappings for the user API.
"""
from django.urls import path

from user import views

#This app name is gonna be userd for the REVERSED MAPPING defined in test_user_api.py
app_name = 'user'

#THAT'S HOW WE enable the APIs
urlpatterns = [
    #Vsaka zahteva, ki bo šla na ta url (create), bo posredovana na "view.CreateUsetView..." (ki smo ga definirali v view.py)
    #Sintaksa je taka, da django pričakuje metodo za na koncu dodamo "as_view()" s katerim vrnemo funkcijo
    #Ime "name='create'" se uporablja za REVERSE LOOKUP (reverse: 'user:create')
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
]
