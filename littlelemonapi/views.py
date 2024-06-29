from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from .permissions import IsAdminOrReadOnly
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer, SimpleMenuItemSerializer

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

    def get_serializer_class(self):
        if self.action == 'list':
            return SimpleMenuItemSerializer
        return self.serializer_class