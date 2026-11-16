
from django.contrib import admin
from .models import PickupRequest


@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "category",
        "quantity",
        "pickup_date",
        "time_slot",
        "status",
    )

    list_filter = ("status", "category", "pickup_date")
    search_fields = ("user__username", "address", "category")
    list_editable = ("status",)
    ordering = ("-created_at",)

from .models import RecyclerProfile

@admin.register(RecyclerProfile)
class RecyclerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "organization",
        "user",
        "phone",
        "approved",
        "applied_at",
    )

    list_filter = ("approved",)
    search_fields = ("organization", "user__username", "phone")
    list_editable = ("approved",)
    ordering = ("-applied_at",)
