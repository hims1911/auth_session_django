import datetime
import logging
import secrets

# from django.urls import reverse
import urllib.parse

import requests
from django.conf import settings
from django.contrib.auth import authenticate
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework import parsers

from accounts.models import User
from accounts.renderers import UserRenderer
from accounts.serializers import (
    UserChangePasswordSerializer,
    UserLoginResponseSerializer,
    UserLoginSerializer,
    UserRegistrationResponseSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserProfilePictureSerializer
)

# from django.shortcuts import render
logger = logging.getLogger(__name__)


# Generate token Manually
class TokenUtility:
    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @staticmethod
    def generate_dummy_jwt_token(Cpayload):
        # creating custom payload with 5 minutes expiration time
        custom_payload = {
            "exp": datetime.datetime.utcnow() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        }
        custom_payload.update(Cpayload)
        # Create a new AccessToken with the custom payload
        access_token = AccessToken()
        access_token.payload.update(custom_payload)
        return str(access_token)

    @staticmethod
    def add_payload(token, payload):
        access_token = AccessToken(token)
        access_token.payload.update(payload)
        return str(access_token)

    @staticmethod
    def verify_and_get_payload(token):
        try:
            # Decode the token and verify its validity
            access_token = AccessToken(token)
            # Getting payload
            payload = access_token.payload
            return payload
        except InvalidToken:
            # Token is invalid
            raise InvalidToken("Invalid token")
        except TokenError:
            # Some other token-related error
            raise TokenError("Token expired")


# Registering the user directly log in the user
class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={200: UserRegistrationResponseSerializer},
        tags=["auth"],
        auth=[],
    )
    def post(self, request):
        """
        Handles user registration and returns JWT tokens upon successful registration.

        This endpoint registers a new user with the provided email, name, and password.
        It also logs the user in immediately by generating and returning JWT tokens.

        :param request: HTTP POST request containing user registration details.
                        Expected fields: email, name, password, password2.

        :return: JSON response containing access and refresh tokens.
                 Example:
                 {
                     "token": {
                         "refresh": "<refresh_token>",
                         "access": "<access_token>"
                     }
                 }
        """
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # returns the user instance

        # optionally set login_method if not done in serializer
        user.login_method = "local"
        user.save(update_fields=["login_method"])

        token = TokenUtility.get_tokens_for_user(user=user)

        return Response(
            {"token": token},
            status=status.HTTP_200_OK,
        )


# Login the user and generate JWT token
class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserLoginResponseSerializer},
        tags=["auth"],
        auth=[],
    )
    def post(self, request):
        """
        Authenticates the user and returns a JWT token upon successful login.

        :param request: HTTP POST request containing user credentials (email and password).
        :return: JSON response with access and refresh tokens and a success message.
                 Example:
                 {
                     "token": {
                         "refresh": "<refresh_token>",
                         "access": "<access_token>"
                     },
                     "msg": "Login Success"
                 }
        """
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")
        user = authenticate(email=email, password=password)

        if user is not None:
            token = TokenUtility.get_tokens_for_user(user)
            return Response(
                {
                    "token": token,
                    "msg": "Login Success",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"errors": {"non_field_errors": ["Email or password is not valid."]}},
                status=status.HTTP_401_UNAUTHORIZED,
            )


# UserProfileView: profile of logged-in user
class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserSerializer},
        tags=["auth"]
    )
    def get(self, request):
        """
        Retrieve the profile information of the authenticated user.

        This endpoint returns the user's profile details such as email, name, and other
        read-only fields defined in the `UserSerializer`.

        Authentication via a valid JWT access token is required.

        :param request: HTTP GET request with a valid JWT token in the Authorization header.
        :return: JSON response containing the user's profile information.
                 Example:
                 {
                     "id": 1,
                     "email": "user@example.com",
                     "name": "John Doe",
                     ...
                 }
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# UserLogOutView: LogOut User
class UserLogOutView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["auth"])
    def post(self, request):
        """
        Logs out the authenticated user by blacklisting their refresh token.
        :param request: HTTP POST request containing the 'refresh_token' in the body.
        :return: JSON response confirming logout or detailing an error.
                 Success Example:
                 {
                     "msg": "LogOut Successfully"
                 }
                 Error Example:
                 {
                     "errors": {
                         "msg": "Token is invalid or expired"
                     }
                 }
        """
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"errors": {"msg": "Refresh token is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token_obj = RefreshToken(refresh_token)
            token_obj.blacklist()
            return Response(
                {"msg": "Logged out successfully."},
                status=status.HTTP_200_OK,
            )
        except TokenError as e:
            return Response(
                {"errors": {"msg": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Password Changed functionality
class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=UserChangePasswordSerializer, tags=["auth"])
    def post(self, request):
        """
        Allows the authenticated user to change their password.

        The user must provide their old password and a new password.
        This endpoint requires authentication via a valid JWT token.

        :param request: HTTP POST with old_password and new_password fields.
        :return: JSON response confirming password change.
        """
        serializer = UserChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"msg": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


# views.py
class UserProfilePictureUpdateView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @extend_schema(
        request=UserProfilePictureSerializer,
        responses={200: UserProfilePictureSerializer},
        tags=["auth"]
    )
    def put(self, request):
        """
        Updates the profile picture of the authenticated user.

        This endpoint allows a logged-in user to upload or change their profile picture.
        The request must be a multipart/form-data containing the image file.

        Expected Request Format (multipart/form-data):
            {
                "profile_picture": <image_file>
            }

        :param request: HTTP PUT request with profile picture in form-data.
        :return: JSON response with the updated user data including the profile
        """
        serializer = UserProfilePictureSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GoogleHandle(APIView):
    renderer_classes = [UserRenderer]

    def get(self, request):
        # creating a random state
        state = secrets.token_urlsafe(32)

        # defining the sessions params
        params = {
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "scope": "openid email profile",
            "state": state,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "response_type": "code",
        }
        request_url = "{}?{}".format(
            "https://accounts.google.com/o/oauth2/v2/auth",
            urllib.parse.urlencode(params),
        )

        # setting  the state in sessions
        request.session["oauth_token"] = state

        return Response({"google_redirect_url": request_url}, status=status.HTTP_200_OK)


class CallbackHandleView(APIView):
    renderer_classes = [UserRenderer]

    def get(self, request):
        access_token = request.query_params.get("access_token")

        if access_token is None:
            return Response(
                {"error": "Invaid request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use the access token to retrieve user information from Google
        user_info_response = requests.get(
            f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
        )
        user_info = user_info_response.json()

        # Extract the email and name from the user information
        email = user_info.get("email", None)
        name = user_info.get("name", None)
        if not email or not name:
            return Response(
                {"error": "Failed to get data from Google user info."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Login the user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "name": name,
                "login_method": "google_login",
                "last_verified_identity": datetime.datetime.now(),
            },
        )
        if not created:
            user.last_verified_identity = datetime.datetime.now()
            user.save()

        jwt_token = TokenUtility.get_tokens_for_user(user)
        return Response(
            {"token": jwt_token, "msg": "Success"}, status=status.HTTP_200_OK
        )
