from django.contrib import admin

from api.models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "date_of_birth", "created"]

    search_fields = ["first_name", "last_name", "date_of_birth"]

    ordering = ["-created"]


admin.site.register(Customer, CustomerAdmin)
