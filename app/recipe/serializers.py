"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Recipe #S tem povemo Django frameworku, da bomo uporabili Recipe model s tem serializer-jem
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']

#Serializer za "podrobnosti recepta" (samo za en zapis).
#OPOMBA: Class naredimo na osnovi zgornjega RecipeSerializer, ker želimo vso funkcionalnost prejšnega, ki pa mu dodamo še nekaj polj.
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

