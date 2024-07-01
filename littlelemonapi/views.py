from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    ListModelMixin
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MenuItemFilter
from .permissions import IsAdminOrReadOnly, IsAdminOrDeliveryCrew
from .paginations import DefaultPagination
from .models import Category, MenuItem, OrderItem, Cart, CartItem, Profile, Order
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    SimpleMenuItemSerializer,
    CartSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
    ProfileSerializer,
    OrderSerializer,
    CreateOrderSerializer,
    UpdateOrderSerializer,
    ProfileSerializerForAdmin,
    ProfileUpdateSerializer
)


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        if MenuItem.objects.filter(category_id=kwargs["pk"]).count() > 0:
            return Response(
                {"error": "category can not be deleted!"},
                status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.select_related("category").all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MenuItemFilter
    pagination_class = DefaultPagination
    ordering_fields = ["price"]
    search_fields = ["title"]

    def get_serializer_class(self):
        if self.action == "list":
            return SimpleMenuItemSerializer
        return self.serializer_class

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(menu_item_id=kwargs["pk"]).count() > 0:
            return Response(
                {"error": "item can not be deleted"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


class CartViewSet(
    CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = Cart.objects.prefetch_related("items__menu_item").all()
    serializer_class = CartSerializer
    permission_classes = [AllowAny]


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [AllowAny]

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"]).select_related(
            "menu_item"
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}


class ProfileViewSet(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = Profile.objects.all()

    @action(detail=False, methods=["GET", "PUT"])
    def me(self, request):
        (profile, created) = Profile.objects.get_or_create(user_id=request.user.id)
        if request.method == "GET":
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = ProfileUpdateSerializer(profile, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return ProfileSerializerForAdmin
        return ProfileSerializer
        
    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return Profile.objects.filter(user_id=self.request.user.id)
    
    def get_permissions(self):
        if self.action == 'retrieve':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        return {"user_id": self.request.user.id}
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Profile.objects.filter(user_id=self.request.user.id).exists():
            raise serializers.ValidationError('profile already exists')
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        elif self.request.user.profile.role == 'D':
            return Order.objects.filter(delivery_crew_id=self.request.user.id)
        else:
            return Order.objects.filter(user_id=self.request.user.id)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        else:
            return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        if self.request.method == 'PATCH':
            return [IsAdminOrDeliveryCrew()]
        return [IsAuthenticated()]