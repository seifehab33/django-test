from django.contrib import admin
from .models import Location, Camera, Person, Community, UsersInCommunity, Camera_History, SecurityPersonnel, Admin

admin.site.register(Location)
admin.site.register(Camera)
admin.site.register(Person)
admin.site.register(Community)
admin.site.register(UsersInCommunity)
admin.site.register(Camera_History)
admin.site.register(SecurityPersonnel)
admin.site.register(Admin)
