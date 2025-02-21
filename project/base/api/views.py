from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import Room_Serializer

# api_view(['GET']) -> this view get_routes is only available for GET requests
@api_view(['GET'])
def get_routes(request):
    routes = [

        'GET /api',
        # Getting list of rooms objects
        'GET /api/rooms', 
        # Getting single room object based on id
        'GET /api/rooms/:id',
    ]

    return Response(routes)

@api_view(['GET'])
def get_rooms(request):
    rooms = Room.objects.all()
    
    # Serialization is needed becasue Response() cannot return python objects
    # many=True -> we are returning multiple rooms
    serializer = Room_Serializer(rooms, many=True)  
    return Response(serializer.data)

@api_view(['GET'])
def get_room(request, pk):
    room = Room.objects.get(id=pk)
    
    # Serialization is needed becasue Response() cannot return python objects
    # many=False -> we are returning single room
    serializer = Room_Serializer(room, many=False)  
    return Response(serializer.data)