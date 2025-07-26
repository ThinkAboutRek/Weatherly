from django.contrib import admin
from .models import Search

@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ("city", "searched_at")
    ordering = ("-searched_at",)
