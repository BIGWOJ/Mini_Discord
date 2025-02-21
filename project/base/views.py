from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
# Using build in user model
# from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Built in UserCreationForm for creating new users
# from django.contrib.auth.forms import UserCreationForm

# Adding User model after changing to using own User model
from .models import Room, Topic, Message, User
from .forms import Room_form, User_form, My_User_Creation_Form

def login_page(request):
    page = 'login'
    # If user is already logged in, redirect to home page from login page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

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
    # Changing to own User model
    # form = UserCreationForm()
    form = My_User_Creation_Form()

    context = {'form': form}

    if request.method == 'POST':
        form = My_User_Creation_Form(request.POST)
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
    # Getting first 5 topics
    topics = Topic.objects.all()[0:5]
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
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        # get_or_create -> if topic exists, get it, if not create it
        # topic -> topic object
        # created -> boolean value, if topic was created, created = True
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )        

        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    #found room based on primary key
    room = Room.objects.get(id=pk)
    #room prefilled with details of specified room
    form = Room_form(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You cannot edit someone elses room')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=
        topic_name)
        # print(topics)
        # print(f'{room.topic} {topics.filter(name=room.topic).count()}')
        # print(f'{topic} {topics.filter(name=topic).count()}')
        # print(f'test nowy {topics.filter(name='test nowy').count()}')
        # if room.topic != topic:


        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        
        
        room.save()
        # if created and :
        # if created:
        #     print(f'Topic "{topic_name}" was created and assigned to the room.')
        # else:
        #     print(f'Topic "{topic_name}" was assigned to the room.')
        
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
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

@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = User_form(instance=user)

    if request.method == "POST":
        # request.FILES -> for image upload (avatar)
        form = User_form(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update_user.html', context)

def topics_page(request):
    if request.GET.get('query') != None:
        query = request.GET.get('query')
    else:
        query = ''
    topics = Topic.objects.filter(name__icontains=query)
    context = {"topics": topics}
    return render(request, 'base/topics.html', context)

def activity_page(request):
    room_messages = Message.objects.all()
    context = {"room_messages": room_messages}
    return render(request, 'base/activity.html', context)