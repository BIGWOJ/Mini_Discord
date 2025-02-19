from django.forms import ModelForm
from .models import Room
from django.contrib.auth.models import User

class Room_form(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        # Exclude host and participants from the form
        exclude = ['host', 'participants']

class User_form(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        