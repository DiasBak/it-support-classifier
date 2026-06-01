from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Ticket


# ============================================
# User Admin
# ============================================
@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            'Role Settings',
            {
                'fields': (
                    'role',
                )
            }
        ),
    )
    list_display = (
        'username',
        'email',
        'role',
        'is_staff',
        'is_superuser'
    )


# ============================================
# Ticket Admin
# ============================================
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'predicted_category',
        'status',
        'priority',
        'created_at'
    )
    list_filter = (
        'status',
        'priority'
    )
    search_fields = (
        'text',
        'predicted_category'
    )