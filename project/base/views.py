from django.shortcuts import render, redirect
from .models import Room, Topic
from .forms import Room_form
from django.db.models import Q

# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Lets learn python'},
#     {'id': 2, 'name': 'Design with me'},
#     {'id': 3, 'name': 'Frontend developers'},
# ]

def home(request):
    #filtering
    #Situation on homepage -> without any filters firstly it showed 0 rooms
    #so if this situation -> show all rooms
    if request.GET.get('query') != None:
        query = request.GET.get('query')
    else:
        query = ''
    #Quering upwards -> querying parent
    #i in icontains - case insensitive
    #contains, e.g. room name Web development, searching we quering positive because Web contains case insensitive 'web'
    #filters can be satisfied with matching room topic, name or description
    rooms = Room.objects.all().filter(
            Q(topic__name__icontains=query) |
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    topics = Topic.objects.all()
    room_count = rooms.count()
    
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room': room}
    return render(request, 'base/room.html', context)

def create_room(request):
    form = Room_form()
    if request.method == 'POST':
        form = Room_form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

def update_room(request, pk):
    #found room based on primary key
    room = Room.objects.get(id=pk)
    #room prefilled with details of specified room
    form = Room_form(instance=room)

    if request.method == 'POST':
        #Replacing room details
        form = Room_form(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        #Removing from database and deleting room
        room.delete()
        return redirect('home')

    context = {'obj': room}
    return render(request, 'base/delete.html', context)