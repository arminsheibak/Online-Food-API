from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet , basename='categories')
router.register('menu-items', views.MenuItemViewSet, basename='menu_items')
router.register('carts', views.CartViewSet, basename='carts')

carts_router = NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(carts_router.urls)),
]