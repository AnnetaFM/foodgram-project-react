from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LEN = 150


class User(AbstractUser):
    username = models.CharField(
        max_length=MAX_LEN,
        verbose_name="Имя пользователя",
        help_text="Введите уникальное имя пользователя",
        unique=True,

    )
    password = models.CharField(
        max_length=MAX_LEN,
        verbose_name="Пароль",
        help_text="Введите пароль",
    )
    email = models.EmailField(
        max_length=254,
        verbose_name="Адрес электронной почты",
        help_text="Введите адрес электронной почты",
        unique=True,
    )
    first_name = models.CharField(
        max_length=MAX_LEN,
        verbose_name="Имя",
        help_text="Введите имя",
    )
    last_name = models.CharField(
        max_length=MAX_LEN,
        verbose_name="Фамилия",
        help_text="Введите фамилию",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['username']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_subscriptions',
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_followers',
        verbose_name="Автор рецепта",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscribe'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='check_user_not_equal_author'
            ),
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
