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
from recipe.serializers import RecipeDetailSerializer

import tempfile,os
from PIL import Image
RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    return reverse('recipe:recipe-detail',args=[recipe_id])

def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image',args = [recipe_id])

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
        other_user = get_user_model().objects.create_user(
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
    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data,serializer.data)

    def test_create_recipe(self):
        payload = {
            'title': 'sample recipe',
            'time_minutes': 40,
            'price': Decimal('10'),
        }
        res = self.client.post(RECIPE_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe,k),v)
        self.assertEqual(recipe.user,self.user)

class Image_Upload_Test(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self) -> None:
        self.recipe.image.delete()
    def test_upload_image(self):
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as img_file:
            img = Image.new('RGB',(10,10))
            img.save(img_file,format='JPEG')
            img_file.seek(0)
            payload = {
                'image':img_file
            }
            res = self.client.post(url,payload ,format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn('image',res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_uploading_bad_image(self):
        url = image_upload_url(self.recipe.id)
        payload = {'image':'not a image'}
        res = self.client.post(url,payload,format='multipart')

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)


