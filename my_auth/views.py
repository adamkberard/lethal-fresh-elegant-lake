from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView

from .serializers import MyLogInSerializer, MyRegisterSerializer

loginResponseSchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties=OrderedDict((
        ("access_token", openapi.Schema(type=openapi.TYPE_STRING)),
    )),
    required=[]
)


class LoginView(CreateAPIView):
    """
    View for authenticating users
    """
    serializer_class = MyLogInSerializer

    @swagger_auto_schema(responses=({200: loginResponseSchema, 400: 'Bad Request'}))
    def post(self, request):
        return super().post(request)


class RegisterView(CreateAPIView):
    """
    View for registering users
    """
    serializer_class = MyRegisterSerializer

    @swagger_auto_schema(responses=({201: loginResponseSchema, 400: 'Bad Request'}))
    def post(self, request):
        return super().post(request)
