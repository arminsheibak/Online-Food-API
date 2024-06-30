from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MenuItemFilter
from .permissions import IsAdminOrReadOnly
from .paginations import DefaultPagination
from .models import Category, MenuItem, OrderItem, Cart, CartItem
from .serializers import CategorySerializer, MenuItemSerializer, SimpleMenuItemSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        if MenuItem.objects.filter(category_id=kwargs['pk']).count() > 0:
            return Response(
                {'error' : 'category can not be deleted!'}, status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().destroy(request, *args, **kwargs)

class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.select_related('category').all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MenuItemFilter
    pagination_class = DefaultPagination
    ordering_fields = ['price']
    search_fields = ['title']

    def get_serializer_class(self):
        if self.action == 'list':
            return SimpleMenuItemSerializer
        return self.serializer_class
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(menu_item_id=kwargs["pk"]).count() > 0:
            return Response(
                {"error": "item can not be deleted"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)
    

class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__menu_item').all()
    serializer_class = CartSerializer
    permission_classes = [AllowAny]


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('menu_item')
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}