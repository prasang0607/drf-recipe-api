from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from core import models
import os


def sample_user(email='test@gmail.com', password='testpass'):
    """ Create a sample user """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """ Test creating a new user with an email is successful """
        email = 'test@gmail.com'
        password = 'TestPass123'
        user = get_user_model(). \
            objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ Test the email for a new user is normalized """
        email = 'test@GMAIL.COM'
        user = get_user_model(). \
            objects.create_user(email=email, password='TestPass123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ Test creating email with no email raises error """
        with self.assertRaises(ValueError):
            get_user_model().objects. \
                create_user(email=None, password='test123')

    def test_create_new_superuser(self):
        """ Test creating a new superuser """
        email = 'test@gmail.com'
        password = 'TestPass123'
        user = get_user_model().objects. \
            create_superuser(email=email, password=password)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """ Test the tag string representation """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(tag.name, str(tag))

    def test_ingredient_str(self):
        """ Test the ingredient string representation """
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """ Test the recipe string representation """
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and Mushroom Sauce',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """ Test that image is saved in the correct location """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid

        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = os.path.join('uploads', 'recipe', f'{uuid}.jpg')

        self.assertEqual(exp_path, file_path)
