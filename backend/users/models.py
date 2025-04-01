from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .constants import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH, USERNAME_MAX_LENGTH


class User(AbstractUser):
    username = models.CharField(
        validators=[UnicodeUsernameValidator()],
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        db_index=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=NAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=NAME_MAX_LENGTH,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='subscription_unique'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='self_subscription_error'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
