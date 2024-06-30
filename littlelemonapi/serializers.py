from .models import Category, MenuItem, Cart, CartItem
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']





class SimpleMenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'category', 'image', 'price']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = MenuItem
        fields = ['id', 'title','category', 'image', 'description', 'price']


class CartItemSerializer(serializers.ModelSerializer):
    menu_item = SimpleMenuItemSerializer()
    class Meta:
        model = CartItem
        fields = ['id', 'menu_item', 'quantity']

class AddCartItemSerializer(serializers.ModelSerializer):
    menu_item_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id', 'menu_item_id', 'quantity']
    
    def validate_menu_item_id(self, value):
        if not MenuItem.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No menu item with the given id')
        return value
    
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        menu_item_id = self.validated_data['menu_item_id']
        quantity = self.validated_data['quantity']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, menu_item_id=menu_item_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        
        return self.instance


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField('get_total_price')
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
    
    def get_total_price(self, cart):
        return sum([item.menu_item.price * item.quantity for item in cart.items.all()])