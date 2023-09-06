from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        verbose_name="Имя пользователя",
        help_text="Введите уникальное имя пользователя",
        unique=True,

    )
    password = models.CharField(
        max_length=150,
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
        max_length=150,
        verbose_name="Имя",
        help_text="Введите имя",
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
        help_text="Введите фамилию",
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


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

    def __str__(self):
        return f"{self.user} подписан на {self.author}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscribe'
            )
        ]
