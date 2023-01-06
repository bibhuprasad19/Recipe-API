"""
tests recipe api
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')

def create_recipe(user,**params):
    """create and retiurn recipe"""

    defaults = {
        'title': 'make matar panner',
        'time_minutes': 5,
        'price': Decimal('10'),
        'description': 'not available',
        'link': 'abjgyfg@example.com',
    }
    defaults.update(params) # we setting a default dic but if we got values in params then we are updating the params

    recipe = Recipe.objects.create(user=user,**defaults)

    return recipe

class PublicRecipeAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_request(self):
        """ authentication required for recipe api"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PriavteRecipeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass@123'
        )
        self.client.force_authenticate(self.user)
    def test_retrieve_recipe(self):
        create_recipe(user = self.user)
        create_recipe(user = self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes,many=True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
    def test_recipe_list_limited_to_user(self):
        other_user = get_user_model().objects.craete_user(
            'other@example.com',
            'password123'
        )
        create_recipe(user = other_user)
        create_recipe(user = self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user = self.user)
        serializer = RecipeSerializer(recipes , many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
