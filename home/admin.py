from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Watch)
admin.site.register(Payment)
admin.site.register(Cart)
admin.site.register(OrderPlaced)
admin.site.register(Wishlist)
admin.site.register(Address)
admin.site.register(WatchImage)