from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.pagination import RecipePagination
from api.recipes.serializers import (
    SubscriptionCreateSerializer,
    SubscriptionSerializer
)
from users.models import Subscription

from .serializers import UserAvatarSerializer, UserSerializer

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = RecipePagination

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
        deleted_count, _ = Subscription.objects.filter(
            user=request.user,
            author=get_object_or_404(User, id=id)
        ).delete()

        if deleted_count == 0:
            raise serializers.ValidationError(
                detail='Подписка не существует',
                code=status.HTTP_400_BAD_REQUEST,
            )

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

    @action(detail=False,
            methods=('PUT',),
            url_path='me/avatar',
            url_name='avatar',
            permission_classes=(permissions.IsAuthenticated,))
    def avatar(self, request):
        serializer = UserAvatarSerializer(self.get_instance(),
                                          data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
