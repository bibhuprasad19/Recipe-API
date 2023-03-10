"""
Tests for Models
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch
from core import models

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        email = 'test@example.com'
        password = 'testpass123'
        user=get_user_model().objects.create_user(
            email=email,
            password = password,

        )
        self.assertEqual(user.email,email)
        self.assertTrue(user.check_password(password))
    def test_new_user_email_normalized(self):
        sample_emails = [
            ["test1@Example.com","test1@example.com"],
            ["Test2@Example.com","Test2@example.com"],
            ["test3@EXAMPLE.com","test3@example.com"],
            ["Test@EXAMPLE.COM","Test@example.com"]
        ]
        for email,expected in  sample_emails:
            user=get_user_model().objects.create_user(email,"sample123")
            self.assertEqual(user.email,expected)
    def test_new_user_without_email_raises_ValueError(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("",'sample12')
    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'sample123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe_successful(self):
        """test new recipe"""
        user = get_user_model().objects.create_user(
            "test@example.com",
            'testpass@123',
        )

        recipe = models.Recipe.objects.create(
            user = user,
            title = 'sample recipe name',
            time_minutes = 5,
            price = Decimal('5.5'),
            description = 'sample recipe description',
        )
        self.assertEqual(str(recipe),recipe.title)
    @patch('core.models.uuid.uuid4')
    def test_recipe_filename_uuid(self,mock_uuid):
        uuid = 'mock-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None,'example.jpg')

        self.assertEqual(file_path,f'uploads/recipe/{uuid}.jpg')
