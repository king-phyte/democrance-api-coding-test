from django.contrib import admin

from api.models import Customer, Policy, PolicyStateHistory, Quote


class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "date_of_birth", "created"]

    search_fields = ["first_name", "last_name", "date_of_birth"]

    ordering = ["-created"]


class QuoteAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "type", "status", "cover", "premium", "created"]

    search_fields = ["type", "customer", "status"]

    ordering = ["-created"]


class PolicyAdmin(admin.ModelAdmin):

    list_display = ["id", "customer", "type", "state", "cover", "premium", "created"]

    search_fields = ["type", "customer", "state"]

    ordering = ["-created"]


class PolicyStateHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "policy_id", "state", "as_json", "created"]

    ordering = ["policy_id", "-created"]

    @admin.display
    def policy_id(self, obj):
        return obj.policy.id


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Policy, PolicyAdmin)
admin.site.register(PolicyStateHistory, PolicyStateHistoryAdmin)
