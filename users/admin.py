# users/admin.py
from django.contrib import admin
from .models import User, Payment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_staff')
    search_fields = ('email',)


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