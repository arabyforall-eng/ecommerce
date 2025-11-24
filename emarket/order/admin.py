from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
list_display = ("get_status_display",)