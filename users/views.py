from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Register berhasil",
            "data": serializer.data
        }, status=201)
    return Response(serializer.errors, status=400)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
