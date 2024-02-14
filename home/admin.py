from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Watch)
admin.site.register(WatchImage)
admin.site.register(OrderPlaced)
admin.site.register(Address)
admin.site.register(Payment)