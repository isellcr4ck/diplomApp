from django.contrib import admin
from .models import User, Currency, Cart, CartItem, Transaction, Review, Feedback
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active', 'avatar_tag')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_staff', 'is_active')
    ordering = ('username',)
    readonly_fields = ('avatar_tag',)
    if BaseUserAdmin.fieldsets:
        fieldsets = BaseUserAdmin.fieldsets + (
            (_('Дополнительно'), {'fields': ('phone', 'avatar')}),
        )
    else:
        fieldsets = (
            (None, {'fields': ('username', 'password', 'email', 'phone', 'avatar')}),
        )
    verbose_name = _('Пользователь')
    verbose_name_plural = _('Пользователи')

    def avatar_tag(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" style="width:40px; height:40px; border-radius:50%; object-fit:cover;" />'
        return ''
    avatar_tag.short_description = 'Аватар'
    avatar_tag.allow_tags = True

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'buy_rate', 'sell_rate', 'change', 'icon_tag')
    search_fields = ('code', 'name')
    list_filter = ('code',)
    ordering = ('name',)
    readonly_fields = ('icon_tag',)
    verbose_name = _('Валюта')
    verbose_name_plural = _('Валюты')

    def icon_tag(self, obj):
        if obj.icon:
            return f'<img src="{obj.icon.url}" style="width:32px; height:32px; border-radius:50%; object-fit:cover;" />'
        return ''
    icon_tag.short_description = 'Иконка'
    icon_tag.allow_tags = True

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    verbose_name = _('Позиция корзины')
    verbose_name_plural = _('Позиции корзины')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username',)
    inlines = [CartItemInline]
    verbose_name = _('Корзина')
    verbose_name_plural = _('Корзины')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'currency', 'amount', 'operation_type', 'rate', 'total', 'status', 'created_at')
    list_filter = ('currency', 'operation_type', 'status', 'created_at')
    search_fields = ('user__username', 'currency__code')
    actions = ['mark_completed', 'mark_pending']
    verbose_name = _('Транзакция')
    verbose_name_plural = _('Транзакции')

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = 'Отметить как завершённые'

    def mark_pending(self, request, queryset):
        queryset.update(status='pending')
    mark_pending.short_description = 'Отметить как в ожидании'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'currency', 'amount', 'operation_type', 'rate', 'added_at')
    list_filter = ('currency', 'operation_type', 'added_at')
    search_fields = ('cart__user__username', 'currency__code')
    verbose_name = _('Позиция корзины')
    verbose_name_plural = _('Позиции корзины')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'rating', 'text', 'created_at', 'is_published')
    list_filter = ('is_published', 'rating', 'created_at')
    search_fields = ('name', 'text', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    actions = ['publish_reviews', 'unpublish_reviews']
    verbose_name = 'Отзыв'
    verbose_name_plural = 'Отзывы'

    @admin.action(description='Опубликовать выбранные отзывы')
    def publish_reviews(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'Опубликовано {updated} отзывов.')

    @admin.action(description='Снять публикацию с выбранных отзывов')
    def unpublish_reviews(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'Снята публикация с {updated} отзывов.')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'email', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    actions = ['mark_processed']
    def mark_processed(self, request, queryset):
        updated = queryset.update(is_processed=True)
        self.message_user(request, f'Отмечено как обработано: {updated} сообщений.')
    mark_processed.short_description = 'Отметить как обработанные'
