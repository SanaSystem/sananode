from django.contrib import admin
from .models import NodeRegistration, UserRegistration
# Register your models here.
admin.site.register(NodeRegistration)
admin.site.register(UserRegistration)