from django.contrib import admin
from .models import MyUser, FeaturedSite


admin.site.register(MyUser)
admin.site.register(FeaturedSite)
