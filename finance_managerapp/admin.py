from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your models here.
from .models import Profile

# admin.site.register(Profile)
class CustomUserAdmin(UserAdmin):
    def has_change_permission(self, request, obj=None):
        if obj and not hasattr(obj, 'profile'):
            return False
        return super().has_change_permission(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)