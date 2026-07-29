import logging

from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.shared.exceptions import CustomException
from apps.shared.utils.response import CustomResponse
from apps.users.serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


@extend_schema(tags=["Auth"])
class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(request=RegisterSerializer, responses={201: UserProfileSerializer}, summary="Register")
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.validation_error(errors=serializer.errors, request=request)

        user = serializer.save()
        logger.info(f"New user registered: {user.phone_number}")

        return CustomResponse.success(
            message_key="USER_REGISTERED",
            request=request,
            data=UserProfileSerializer(user).data,
        )


@extend_schema(tags=["Auth"])
class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(request=LoginSerializer, responses={200: UserProfileSerializer}, summary="Login")
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.validation_error(errors=serializer.errors, request=request)

        user = authenticate(
            request,
            username=serializer.validated_data["phone_number"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            raise CustomException("INVALID_CREDENTIALS")

        if not user.is_active:
            raise CustomException("USER_INACTIVE")

        tokens = _get_tokens(user)
        logger.info(f"User logged in: {user.phone_number}")

        return CustomResponse.success(
            message_key="SUCCESS",
            request=request,
            data={**UserProfileSerializer(user).data, **tokens},
        )


@extend_schema(tags=["Auth"])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    @extend_schema(summary="Logout — blacklists refresh token")
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return CustomResponse.success(message_key="LOGGED_OUT", request=request)


@extend_schema(tags=["Auth"])
class MeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    @extend_schema(responses={200: UserProfileSerializer}, summary="Current user profile")
    def get(self, request):
        return CustomResponse.success(
            message_key="SUCCESS",
            request=request,
            data=UserProfileSerializer(request.user).data,
        )


def _get_tokens(user) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}