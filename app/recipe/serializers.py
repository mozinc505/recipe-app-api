"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)

#OPOMBA: Mora biti pred RecipeSerializer-jem, ker ga ta uporablja (nested)
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer foringredients."""

    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe #S tem povemo Django frameworku, da bomo uporabili Recipe model s tem serializer-jem
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags',
            'ingredients'
            ]
        read_only_fields = ['id']

    #Naredimo pomožno metodo
    #OPOMBA: Interne metode označimo s podčrtajem v imenu.
    #Pomeni, da želimo, da se metoda uporablja samo v tem class-u
    #Pomeni, da želimo da je "private" (ni pa tehnično to res "private" - še vedno jo lahko kličemo od zunaj - samo dogovor je tak)
    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context["request"].user
        for ingredient in ingredients:
            #Dodamo zapis v šifrant (ingredients)
            ingredient_obj, create = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            #Povežemo zapis z receptom (relacija)
            recipe.ingredients.add(ingredient_obj)



    #OPOMBA: Ker so "nested" serializer-ji po defaultu READ-ONLY, mi pa želimo tudi dodajati tag-e, moramo
    #narediti override te metode
    def create(self, validated_data):
        """Create a recipe."""
        #Naredimo custom logiko za kreiranje objekta preko tega serializer-ja

        #Poberemo ven tag-e in jih odstranimo iz seznama
        tags = validated_data.pop('tags', []) #Drugi parameter --> določa default, če ni tega podatka --> torej prazen seznam

        ingredients = validated_data.pop("ingredients", [])

        #Naredimo recept
        recipe = Recipe.objects.create(**validated_data) #Na tem mestu validated_data nimamo več tags-ov in ingredients-ov

        #Poberemo user-ja (ker delamo znotraj serializer-ja, da moramo pobrati na ta način)
        #Context je posredovan serializer-ju s strani view-ja na katerega je zvezan

        #auth_user = self.context["request"].user #S tem poberemo avtenticiranega uporabnika

        #for tag in tags:
            ##get_or_create metoda je helper metoda znotraj ModelManager-ja (ki se pri modelih imenuje objects).
            ##VRNE: Touple (kreiran objekt in True/False - ali je bil objekt narejen)

            #tag_obj, created = Tag.objects.get_or_create( #Ta metoda nam omogoča, da ne naredimo duplikatov v sistemu in bazi
            #    user = auth_user,
            #    **tag,
            #    #name=tag["name"] #Uporabimo **tag, da ne zapečemo točno na določena polja
            #)
            #recipe.tags.add(tag_obj)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    #OPOMBA: Z override te metode omogočimo ažuriranje vgnezdenih serializer-jev
    def update(self, instance, validated_data):
        """Update recipe."""

        """
        instance --> je trenutna instanca, ki se update-a
        validated_data --> so podatki s katerimi se instanca update-a
        """

        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        ingredients = validated_data.pop("ingredients", None)
        if ingredients is not None:
            #OPOMBA: Tole se izvede samo, če smo dobili "ingredients" med parametri.
            #V nasprotnem primeru smo nastavili vrednost na None.
            #Dopuščamo da dobimo prazen seznam in na osnovi tega "pobrišemo" ingredients z recepta.
            instance.ingredients.clear() #Zrišemo obstoječe
            self._get_or_create_ingredients(ingredients, instance) #Nastavimo nove

        #Vse preostale podatke apliciramo na recept
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


#Serializer za "podrobnosti recepta" (samo za en zapis).
#OPOMBA: Class naredimo na osnovi zgornjega RecipeSerializer, ker želimo vso funkcionalnost prejšnega, ki pa mu dodamo še nekaj polj.
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe detail view."""

    class Meta(RecipeSerializer.Meta): #We pass all the metadata from RecipeSerializer
        fields = RecipeSerializer.Meta.fields + ['description', 'image']


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    """
    Here we're creating a separate serializer and the reason we're trying to
    separate serialize it is because when we upload images we only need to accepts the image field.
    """

    """
    We're doing this as a separate API, and the reason why we do it as a separate API is because it's best
    practice to only upload one type of data to an API.
    So we don't want to be uploading a form data which contains all the form data of a recipe as well as
    an image.

    We want to have a specific separate API just for handling the image upload to make our API data structures
    clean and easy to use and understand.
    """
    class Meta:
        model = Recipe
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": "True"}}

