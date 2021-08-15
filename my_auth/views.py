from rest_framework.generics import CreateAPIView

from .serializers import MyLogInSerializer, MyRegisterSerializer


class LoginView(CreateAPIView):
    """
    View for authenticating users
    """
    serializer_class = MyLogInSerializer


class RegisterView(CreateAPIView):
    """
    View for registering users
    """
    serializer_class = MyRegisterSerializer
