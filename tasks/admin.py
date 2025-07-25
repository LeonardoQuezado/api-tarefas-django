from django.contrib import admin
from .models import Category, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'execution_date', 'created_at']
    list_filter = ['status', 'categories', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at']
    filter_horizontal = ['categories']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('categories')