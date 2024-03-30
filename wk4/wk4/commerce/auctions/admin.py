from django.contrib import admin
from .models import Listing, Comment, Bid

class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'starting_bid', 'is_active')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('listing', 'user', 'timestamp')

class BidAdmin(admin.ModelAdmin):
    list_display = ('listing', 'bidder', 'amount', 'timestamp')

admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
