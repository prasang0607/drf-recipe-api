from rest_framework import serializers
from core import models


class TagSerializer(serializers.ModelSerializer):
    """ Serializer for tag objects """

    class Meta:
        model = models.Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """ Serializer for ingredient object """

    class Meta:
        model = models.Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """ Serializer for recipe object """
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all(),
        many=True
    )

    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True
    )

    class Meta:
        model = models.Recipe
        exclude = ('user',)
        read_only_fields = ('id',)
