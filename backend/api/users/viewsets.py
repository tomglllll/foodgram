from djoser.views import UserViewSet as DjoserUserViewSet
from .serializers import UserSerializer
from users.models import User


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
