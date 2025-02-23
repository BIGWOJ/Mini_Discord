from django.contrib import admin

# Register your models here.

from .models import Room, Topic, Message, User

# Adding User model to admin panel after creating custom User model
admin.site.register(User)

admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)