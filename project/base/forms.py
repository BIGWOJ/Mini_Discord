from django.forms import ModelForm
from .models import Room

class Room_form(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        # Exclude host and participants from the form
        exclude = ['host', 'participants']