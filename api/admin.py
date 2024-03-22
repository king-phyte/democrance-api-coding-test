from django.contrib import admin

from api.models import Customer, Quote


class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "date_of_birth", "created"]

    search_fields = ["first_name", "last_name", "date_of_birth"]

    ordering = ["-created"]


class QuoteAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "type", "status", "cover", "premium", "created"]

    search_fields = ["type", "customer", "status"]

    ordering = ["-created"]


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Quote, QuoteAdmin)
