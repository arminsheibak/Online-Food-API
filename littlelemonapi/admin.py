from django.contrib import admin
from .models import Category, MenuItem, Order, OrderItem, Profile

admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Profile)


class OrderItemInline(admin.StackedInline):
    model = OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
