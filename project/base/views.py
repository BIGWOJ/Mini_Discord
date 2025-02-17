from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import Room_form

# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Lets learn python'},
#     {'id': 2, 'name': 'Design with me'},
#     {'id': 3, 'name': 'Frontend developers'},
# ]

def login_page(request):
    page = 'login'
    # If user is already logged in, redirect to home page from login page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logout_user(request):
    logout(request)
    return redirect('home')

def register_page(request):
    form = UserCreationForm()
    context = {'form': form}

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Commit=false -> not saving to database yet, firstly clearing up data and logging up on the page
            user = form.save(commit=False)
            user.username = user.username
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Something went wrong during registration')

    return render(request, 'base/login_register.html', context)
 
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
    room_messages = Message.objects.all().filter(Q(room__topic__name__icontains=query))
    
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    # Quering all child objects (messages) of room class (class Messages)
    # class name (Room) has to be lowercase

    # _set.all() for many to one relationship
    # .all() for many to many relationship
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            # <input type="text" name="body" placeholder="Comment...">
            # 'body' from room.html file input name
            body=request.POST.get('body')
        )
        # Adding user to participants after sending a message
        room.participants.add(request.user)
        # Redirecting to the room page after sending a message
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

#Redirecting to login page if user is not logged in
@login_required(login_url='login')
def create_room(request):
    form = Room_form()
    if request.method == 'POST':
        form = Room_form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

#Redirecting to login page if user is not logged in
@login_required(login_url='login')
def update_room(request, pk):
    #found room based on primary key
    room = Room.objects.get(id=pk)
    #room prefilled with details of specified room
    form = Room_form(instance=room)

    if request.user != room.host:
        return HttpResponse('You cannot edit someone elses room')

    if request.method == 'POST':
        #Replacing room details
        form = Room_form(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You cannot delete someone elses room')

    if request.method == 'POST':
        #Removing from database and deleting room
        room.delete()
        return redirect('home')

    context = {'obj': room}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You cannot delete someone elses message')

    if request.method == 'POST':
        #Removing from database and deleting room
        message.delete()
        return redirect('home')

    context = {'obj': message}
    return render(request, 'base/delete.html', context)