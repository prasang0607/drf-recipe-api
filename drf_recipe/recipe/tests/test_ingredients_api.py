from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """ Test the publicly available ingredients API """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is required to access the endpoint """
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """ Test the private ingredients API """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@outlook.com',
            password='TestPass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """ Test retrieving a list of ingredients """
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ Test ingredients are limited to user """
        user = get_user_model().objects.create_user(
            email='other@hotmail.com',
            password='TestPass'
        )

        Ingredient.objects.create(user=user, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user,
                                               name='Turmeric')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """ Test creating a new ingredient """
        payload = {'name': 'Cabbage'}

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = Ingredient.objects. \
            filter(user=self.user, name=payload['name']).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """ Test creating invalid ingredient fails """
        payload = {'name': ''}

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
