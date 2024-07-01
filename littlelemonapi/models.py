from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from uuid import uuid4



class Category(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='menu_items')
    image = models.ImageField(upload_to='images', default='images/default.jpg')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['category']

    def __str__(self) -> str:
        return self.title

class Profile(models.Model):
    class RoleChoice(models.TextChoices):
        CUSTOMER = 'C', _('customer')
        DELIVERY_CREW = 'D', _('delivery_crew')
        ADMIN = 'A', _('admin')

    user = models.OneToOneField(get_user_model(), primary_key=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=510)
    phone = models.CharField(max_length=14)
    birth_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=1, choices=RoleChoice, default=RoleChoice.CUSTOMER)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='orders')
    delivery_crew = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True)
    delivered = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self) -> str:
        return f"Order by {str(self.user.profile)}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.menu_item.title} x {self.quantity}"

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [["cart", "menu_item"]]