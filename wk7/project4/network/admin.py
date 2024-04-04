from django.contrib import admin
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('creator', 'timestamp', 'content')  # Adjusted to match the fields in the Post model
    search_fields = ['content']  # Assuming you want to search by content


admin.site.register(Post, PostAdmin)

