from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from accounts.views import (
    CallbackHandleView,
    GoogleHandle,
    UserChangePasswordView,
    UserLoginView,
    UserLogOutView,
    UserProfileView,
    UserRegistrationView,
    UserProfilePictureUpdateView,
)

app_name = "accounts"

urlpatterns = [
    # Generate Access Token using Refresh Token
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("logout/", UserLogOutView.as_view(), name="logout"),
    path("change-password/", UserChangePasswordView.as_view(), name="change-password"),
    path("update-profile-picture/", UserProfilePictureUpdateView.as_view(), name="update-profile-picture"),

    # TODO: google oauth endpoints, as it will not work on localhost it needs redirection and google account setup
    path("google/login/", GoogleHandle.as_view(), name="google"),
    path("google/login/callback/", CallbackHandleView.as_view(), name="callback"),
]
