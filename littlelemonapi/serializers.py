from django.db import transaction
from rest_framework import serializers
from .models import Category, MenuItem, Cart, CartItem, Profile, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title"]


class SimpleMenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = MenuItem
        fields = ["id", "title", "category", "image", "price"]


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = MenuItem
        fields = ["id", "title", "category", "image", "description", "price"]


class CartItemSerializer(serializers.ModelSerializer):
    menu_item = SimpleMenuItemSerializer()

    class Meta:
        model = CartItem
        fields = ["id", "menu_item", "quantity"]


class AddCartItemSerializer(serializers.ModelSerializer):
    menu_item_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ["id", "menu_item_id", "quantity"]

    def validate_menu_item_id(self, value):
        if not MenuItem.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No menu item with the given id")
        return value

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        menu_item_id = self.validated_data["menu_item_id"]
        quantity = self.validated_data["quantity"]
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, menu_item_id=menu_item_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )

        return self.instance


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField("get_total_price")

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]

    def get_total_price(self, cart):
        return sum([item.menu_item.price * item.quantity for item in cart.items.all()])


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user_id",
            "first_name",
            "last_name",
            "address",
            "phone",
            "birth_date",
        ]

    def save(self, **kwargs):
        user_id = self.context["user_id"]
        self.instance = Profile.objects.create(user_id=user_id, **self.validated_data)
        return self.instance

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["first_name","last_name","address","phone","birth_date"]

class ProfileSerializerForAdmin(serializers.ModelSerializer):
    """To enable admins to change a user's role to delivery crew"""

    class Meta:
        model = Profile
        fields = [
            "user_id",
            "first_name",
            "last_name",
            "address",
            "phone",
            "birth_date",
            "role",
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = SimpleMenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "delivered", "items", "time", "total_price"]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError("No cart with the given id")
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("Cart is Empty")
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]
            user_id = self.context["user_id"]
            cart_items = CartItem.objects.filter(cart_id=cart_id).select_related(
                "menu_item"
            )
            total_price = sum(
                [item.menu_item.price * item.quantity for item in cart_items]
            )
            order = Order.objects.create(user_id=user_id, total_price=total_price)
            order_items = [
                OrderItem(
                    order=order,
                    menu_item=item.menu_item,
                    price=item.menu_item.price,
                    quantity=item.quantity,
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()
            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["delivered"]
