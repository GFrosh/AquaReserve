"""Views for authentication."""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, tokens_for_user


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({
        'user': UserSerializer(user).data,
        'tokens': tokens_for_user(user),
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    return Response({
        'user': UserSerializer(user).data,
        'tokens': tokens_for_user(user),
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    try:
        refresh = request.data.get('refresh')
        if refresh:
            token = RefreshToken(refresh)
            token.blacklist()
    except Exception:
        pass
    return Response({'detail': 'Logged out.'})


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


class UserListView(generics.ListAPIView):
    """Admin endpoint to list all users."""
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-created_at')

    def get_permissions(self):
        return [permissions.IsAdminUser()]
