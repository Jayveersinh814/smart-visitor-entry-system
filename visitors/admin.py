from django.contrib import admin
from .models import Gate, ScanEvent, VisitorPass, Watchlist


@admin.register(Gate)
class GateAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")


@admin.register(VisitorPass)
class VisitorPassAdmin(admin.ModelAdmin):
    list_display = ("visitor_name", "host", "status", "valid_from", "valid_until", "is_multi_entry")
    list_filter = ("status", "is_multi_entry", "visitor_type")
    search_fields = ("visitor_name", "phone_number", "email", "reference_by")


@admin.register(ScanEvent)
class ScanEventAdmin(admin.ModelAdmin):
    list_display = ("visitor_pass", "action", "gate", "scanned_by", "result", "scanned_at")
    list_filter = ("action", "gate")


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number", "email", "reason", "is_active")
    list_filter = ("is_active",)
