from django.test import TestCase
from django.contrib.auth import get_user_model


class TestUserModel(TestCase):

    def test_create_user_with_email_successful(self):
        user = get_user_model().objects.create_user(
            email = 'test@email.com',
            password = 'testpassword123',
        )

        self.assertEqual(user.email, 'test@email.com')
        self.assertTrue(user.check_password('testpassword123'))
    
    def test_new_user_email_normalized(self):
        email = 'test@EMIil.coM'
        user = get_user_model().objects.create_user(email=email, password='password')
        
        self.assertEqual(user.email, email.lower())
    
    def test_create_user_without_email_fails(self):
        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_user(email=None, password='test123')
    
    def test_create_superuser_successful(self):
        superuser= get_user_model().objects.create_superuser(
            email='admin@email.com', password='iamsuperuser'
        )

        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)