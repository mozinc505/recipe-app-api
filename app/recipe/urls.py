"""
URL mappings for the recipe app.
"""
from django.urls import (
    path, #omogoča, da definiramo "path"
    include, #omogoča, da vključimo URL-je po URL imenih
)

#Default router , ki ga zagotavlja Django REST Framework.
#And you can use this with an API view to automatically create routes for all of the different options
#available for that view.
from rest_framework.routers import DefaultRouter


from recipe import views


router = DefaultRouter()

#Registriramo naš viewset pri tem router-ju z imenom "recipes".
#So what that will do is it will create a new endpoint API: api/recipes
#and it will assign all of the different endpoints from our recipe view set to that endpoint.

#Basically what it means is that the recipe viewset is going to have auto generated URLs depending on
#the functionality that's enabled on the view set.
#Because we're using the model viewset, it's going to support all the available methods for create,
#read, update and delete. Those HTTP GET, POST, PUT, PATH and DELETE.
#It will create and register endpoints for each of those options.

router.register('recipes', views.RecipeViewSet)

#We define the name which is used to identify the name when we're doing the reverse lookup of URLs.
app_name = 'recipe'

#And then here in the URL patterns, we're using the include function to include the URLs that are generated
#automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]