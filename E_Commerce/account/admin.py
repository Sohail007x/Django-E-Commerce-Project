from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import User

# Custom User Admin for the User model
class UserModelAdmin(UserAdmin):
    """
    Custom admin configuration for the User model.
    """
    model = User

    # Fields to be displayed in the list view of the admin
    list_display = [
        'id', 'name', 'email', 'is_active', 'is_superuser', 'is_staff', 'is_customer', 'is_seller'
    ]

    # Filters available in the admin list view
    list_filter = ['is_superuser', 'is_staff', 'is_active', 'is_customer', 'is_seller']

    # Field groups to organize the admin form layout
    fieldsets = [
        ('User Credentials', {'fields': ['email', 'password']}),  # Authentication fields
        ('Personal Information', {'fields': ['name', 'city']}),  # User-specific fields
        ('Permissions', {'fields': ['is_active', 'is_staff', 'is_superuser', 'is_customer', 'is_seller']}),  # Permission flags
        ('Timestamps', {'fields': ['created_at', 'updated_at'], 'classes': ['collapse']}),  # Metadata
    ]

    # Fields for creating a new user in the admin panel
    add_fieldsets = [
        (None, {
            'classes': ('wide',),
            'fields': ['email', 'password1', 'password2'],  # Password confirmation for new users
        }),
    ]

    # Fields to be displayed as read-only in the admin form
    readonly_fields = ['created_at', 'updated_at']

    # Fields that can be searched in the admin search bar
    search_fields = ['email', 'name']

    # Default ordering for the admin list view
    ordering = ['email', 'id']

    # Additional configuration for horizontal filters
    filter_horizontal = []

# Register the User model with the custom admin
admin.site.register(User, UserModelAdmin)
