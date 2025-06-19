from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_('Электронная почта'), unique=True)
    phone = models.CharField(_('Телефон'), max_length=20, blank=True, null=True)
    avatar = models.ImageField(_('Аватар'), upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

class Currency(models.Model):
    code = models.CharField(_('Код'), max_length=3, unique=True)
    name = models.CharField(_('Название'), max_length=100)
    buy_rate = models.DecimalField(_('Курс покупки'), max_digits=10, decimal_places=2)
    sell_rate = models.DecimalField(_('Курс продажи'), max_digits=10, decimal_places=2)
    change = models.DecimalField(_('Изменение'), max_digits=5, decimal_places=2)
    icon = models.ImageField(_('Иконка'), upload_to='currency_icons/', blank=True, null=True)

    class Meta:
        verbose_name = _('Валюта')
        verbose_name_plural = _('Валюты')

    def __str__(self):
        return f"{self.name} ({self.code})"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    created_at = models.DateTimeField(_('Создана'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлена'), auto_now=True)
    is_active = models.BooleanField(_('Активна'), default=True)

    class Meta:
        verbose_name = _('Корзина')
        verbose_name_plural = _('Корзины')

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name=_('Корзина'))
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, verbose_name=_('Валюта'))
    amount = models.DecimalField(_('Сумма'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    operation_type = models.CharField(_('Операция'), max_length=10, choices=[('buy', _('Покупка')), ('sell', _('Продажа'))])
    rate = models.DecimalField(_('Курс'), max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(_('Добавлено'), auto_now_add=True)

    class Meta:
        verbose_name = _('Позиция корзины')
        verbose_name_plural = _('Позиции корзины')

    @property
    def total(self):
        return float(self.amount) * float(self.rate)

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, verbose_name=_('Валюта'))
    amount = models.DecimalField(_('Сумма'), max_digits=10, decimal_places=2)
    operation_type = models.CharField(_('Операция'), max_length=10)
    rate = models.DecimalField(_('Курс'), max_digits=10, decimal_places=2)
    total = models.DecimalField(_('Итого'), max_digits=15, decimal_places=2)
    status = models.CharField(_('Статус'), max_length=20, default='pending')
    created_at = models.DateTimeField(_('Создана'), auto_now_add=True)

    class Meta:
        verbose_name = _('Транзакция')
        verbose_name_plural = _('Транзакции')

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Пользователь'))
    name = models.CharField(_('Имя'), max_length=100)
    text = models.TextField(_('Текст отзыва'))
    created_at = models.DateTimeField(_('Дата отзыва'), auto_now_add=True)
    rating = models.PositiveSmallIntegerField(_('Оценка'), default=5)
    is_published = models.BooleanField(_('Опубликован'), default=True)

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}: {self.text[:30]}..."

class Feedback(models.Model):
    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    message = models.TextField('Сообщение')
    created_at = models.DateTimeField('Дата отправки', auto_now_add=True)
    is_processed = models.BooleanField('Обработано', default=False)

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратная связь'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"