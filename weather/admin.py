from django.contrib import admin
from .models import Search


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ("city", "user", "searched_at")
    list_filter = ("searched_at", "user")
    search_fields = ("city", "user__username")
    ordering = ("-searched_at",)
    date_hierarchy = "searched_at"
    readonly_fields = ("searched_at",)
