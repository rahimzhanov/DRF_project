# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Payment


class UserAdmin(BaseUserAdmin):
    """
    Кастомная админка для модели User
    """
    list_display = ('email', 'phone', 'city', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('email', 'phone')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Персональная информация'), {'fields': ('phone', 'city', 'avatar')}),
        (_('Права доступа'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone', 'city'),
        }),
    )


admin.site.register(User, UserAdmin)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_paid_item', 'amount', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('user__email',)

    def get_paid_item(self, obj):
        if obj.paid_course:
            return f"Курс: {obj.paid_course.title}"
        elif obj.paid_lesson:
            return f"Урок: {obj.paid_lesson.title}"
        return "-"

    get_paid_item.short_description = 'Оплачено'