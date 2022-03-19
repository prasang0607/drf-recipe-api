from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient, Recipe
from recipe import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """ Base view set for user owned recipe attributes """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """ Return objects for current authenticated user only """
        assigned_only = self.request.query_params.get('assigned_only', 0)
        assigned_only = bool(int(assigned_only))
        queryset = self.queryset.filter(user=self.request.user)
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.distinct().order_by('-name')

    def perform_create(self, serializer):
        """ Create a new object """
        return serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """ Manage tags in the database """
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """ Manage ingredients in the database """
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """ Manage recipes in the database """
    serializer_class = serializers.RecipeSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Recipe.objects.all()

    def _params_to_ints(self, qs: str):
        """ Convert a list of string IDs to a list of integers """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """ Retrieve recipes for authenticated user """
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset.filter(user=self.request.user)

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.distinct().order_by('id')

    def get_serializer_class(self):
        """ Return appropriate serializer class """
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new recipe """
        serializer.save(user=self.request.user)

    # URL: /api/recipe/recipes/{id}/upload-image
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """ Upload an image to a recipe """
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe, data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
