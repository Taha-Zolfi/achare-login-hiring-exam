from django.contrib import admin
from .models import CustomUser, FailedLoginAttempt

admin.site.register(CustomUser)
admin.site.register(FailedLoginAttempt)
