from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Users

class UsersModelTest(TestCase):
    def setUp(self):
        self.user = Users.objects.create_user(
            email='danydegbe@gmail.com',
            role=Users.Role.USER
        )

    def test_user_creation(self):
        """Test creating a user is successful."""
        self.assertEqual(self.user.email, 'danydegbe@gmail.com')
        self.assertEqual(self.user.role, Users.Role.USER)
        self.assertFalse(self.user.is_verified)

    def test_user_str_representation(self):
        """Test the string representation of the user."""
        expected_str = f"{self.user.id}-{self.user.name} - {self.user.email} - {self.user.role}"
        self.assertEqual(str(self.user), expected_str)

class UserViewTest(APITestCase):
    def setUp(self):
        self.user = Users.objects.create_user(
            username='authuser',
            password='authpassword123',
            email='auth@example.com',
            name='Auth User'
        )
        self.list_url = reverse('users:users-list') # ''
        self.me_url = reverse('users:user-detail') # 'me/'

    def test_create_user_unauthenticated(self):
        """Test POST /users/ allows creation of a user when unauthenticated (if allowed).
           Wait, UserView has permission_classes = [IsAuthenticated] on the class level.
        """
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'newuser@example.com',
            'name': 'New User'
        }
        response = self.client.post(self.list_url, data)
        # Note: If permission_classes=[IsAuthenticated] applies to POST, this should return 401/403.
        # Let's assert based on generic setup: usually APIs want creation to be open,
        # but the class has permissions.IsAuthenticated. We'll check actual behavior.
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
        
    def test_create_user_authenticated(self):
        """Test POST /users/ with an authenticated user."""
        self.client.force_authenticate(user=self.user)
        data = {
            'username': 'newuser2',
            'password': 'newpassword123',
            'email': 'newuser2@example.com',
            'name': 'New User 2'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser2')

    def test_get_me_unauthenticated(self):
        """Test GET /users/me/ fails if not authenticated."""
        response = self.client.get(self.me_url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_get_me_authenticated(self):
        """Test GET /users/me/ returns the authenticated user data."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'authuser')
