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

# View for logging in a user
class LoginView(CreateAPIView):
    serializer_class = MyLogInSerializer

    @swagger_auto_schema(responses=({201: loginResponseSchema}))
    def post(self, request):
        """Logs in user and responds with an access token."""
        return super().post(request)

# View for registering users
class RegisterView(CreateAPIView):    
    serializer_class = MyRegisterSerializer

    @swagger_auto_schema(responses=({201: loginResponseSchema, 400: 'Bad Request'}))
    def post(self, request):
        """Creates a new user and responds with an access token."""
        return super().post(request)
