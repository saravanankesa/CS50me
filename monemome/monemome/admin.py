from django.contrib import admin
from .models import Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'transaction_type', 'value_score']
    list_filter = ['transaction_type', 'value_score']
    search_fields = ['category_name']

admin.site.register(Category, CategoryAdmin)
