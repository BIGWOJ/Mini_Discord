from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm

# Form for creating a new user based on own, not built in User model
class My_User_Creation_Form(UserCreationForm):
    class Meta:
        model = User
        # password1 and password2 are built in fields for password and password confirmation
        fields = ['name', 'username', 'email', 'password1', 'password2']

class Room_form(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        # Exclude host and participants from the form
        exclude = ['host', 'participants']

class User_form(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']
        