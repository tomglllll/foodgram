from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import UserSerializer
from api.recipes.serializers import SubscriptionSerializer, SubscriptionCreateSerializer
from api.recipes.pagination import CustomPagination
from users.models import Subscription, User


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(detail=True,
            methods=('POST',),
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)

        serializer = SubscriptionCreateSerializer(
            data={'author': author.id,
                  'user': request.user.id},
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        follow = get_object_or_404(Subscription,
                                   user=request.user,
                                   author=get_object_or_404(User, id=id))
        follow.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=('GET',),
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        curr_subscriptions = User.objects.filter(following__user=request.user)

        serializer = SubscriptionSerializer(
            self.paginate_queryset(curr_subscriptions),
            context={
                'request': request
            },
            many=True,
        )

        return self.get_paginated_response(serializer.data)
