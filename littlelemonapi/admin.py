from django.contrib import admin
from .models import Category, MenuItem, Order, OrderItem, Profile

admin.site.register(Category)


class OrderItemInline(admin.StackedInline):
    model = OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','user','delivered']
    list_per_page = 20
    list_filter = ['delivered']
    inlines = [OrderItemInline]
    ordering = ['-id']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category']
    list_editable = ['price', 'category']
    list_select_related = ['category']
    ordering = ['category']
    list_per_page = 10



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'role']
    list_editable = ['role']
    list_per_page = 10
    list_filter = ['role']
    ordering = ['role', 'first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']
