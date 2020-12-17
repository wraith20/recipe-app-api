from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGRERDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientAapiTest(TestCase):
    """Test the publicly available ingeredient API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is requried to access the endpoint"""
        res = self.client.get(INGRERDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Test Ingredient can be retrieved by authorzied user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrievieng a list of Ingredient"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGRERDIENT_URL)

        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """"Test that ingredient for the authenticted user"""
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'testpass'
        )
        Ingredient.objects.create(user=user2, name='Vinger')
        ingredient = Ingredient.objects.create(user=self.user, name='Tumeric')

        res = self.client.get(INGRERDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)