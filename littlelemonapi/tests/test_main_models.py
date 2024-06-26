from django.test import TestCase
from django.contrib.auth import get_user_model
from littlelemonapi import models


def sample_user(email="test@email.com", password="testpassword123"):
    return get_user_model().objects.create_user(email, password)


class TestModel(TestCase):

    def test_category_str(self):
        category = models.Category.objects.create(title="chinese")

        self.assertEqual(str(category), "chinese")

    def test_menuitem_str(self):
        category = models.Category.objects.create(title="chinese")
        menu_item = models.MenuItem.objects.create(
            title="chicken",
            category=category,
            price=12.34,
        )

        self.assertEqual(str(menu_item), "chicken")

    def test_profile_str(self):
        profile = models.Profile.objects.create(
            user=sample_user(),
            first_name="John",
            last_name="Smith",
            address="blah blah",
            phone="+123456789",
        )

        self.assertEqual(str(profile), "John Smith")

    def test_order_str(self):
        user = sample_user()
        profile = models.Profile.objects.create(
            user=user,
            first_name="John",
            last_name="Smith",
            address="blah blah",
            phone="+123456789",
        )
        order = models.Order.objects.create(
            user=user,
            delivery_crew=sample_user(email="fff@email.com"),
            total_price=22.00,
        )

        self.assertEqual(str(order), f"Order by John Smith")

    def test_order_item_str(self):
        menu_item = models.MenuItem.objects.create(
            title="pasta",
            category=models.Category.objects.create(title="chinese"),
            price=12.34,
        )
        order_item = models.OrderItem.objects.create(
            order=models.Order.objects.create(
                user=sample_user(),
                delivery_crew=sample_user(email="fff@email.com"),
                total_price=22.00,
            ),
            menu_item=menu_item,
            quantity=4,
            price=12.34,
        )

        self.assertEqual(str(order_item), "pasta x 4")

    def test_cart(self):
        models.Cart.objects.create()
        carts_count = models.Cart.objects.count()

        self.assertEqual(carts_count, 1)

    def test_cart_item(self):
        cart_item = models.CartItem.objects.create(
            cart=models.Cart.objects.create(),
            menu_item=models.MenuItem.objects.create(
                title="pasta",
                category=models.Category.objects.create(title="chinese"),
                price=12.34,
            ),
            quantity=8,
        )

        count = models.CartItem.objects.count()
        self.assertEqual(count, 1)
