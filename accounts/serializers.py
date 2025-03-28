from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from accounts.models import User
from django.core.exceptions import ValidationError as DjangoValidationError


# from apps.accounts.views import generate_guest_token


# User registration
class UserRegistrationSerializer(serializers.ModelSerializer):
    # Confirm password field
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["email", "name", "password", "password2"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    # Password match validation
    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError("Password and Confirm Password don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")  # Remove confirm password
        user = User.objects.create_user(**validated_data)
        user.login_method = "local"  # Optional: if you want to centralize this
        user.save(update_fields=["login_method"])
        return user


class UserRegistrationResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


# Login the user
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ["email", "password"]


class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class UserLoginResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


# Serializer for showing User profile
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "slug",
            "image"
        ]


# UserChangePasswordSerializer for providing change password functionality to logged-in user
class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        fields = ["password", "password2"]

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        user = self.context.get("user")

        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password do not match.")

        if user.check_password(password):
            raise serializers.ValidationError("New password cannot be the same as the old password.")

        try:
            validate_password(password, user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)

        return attrs

    def save(self, **kwargs):
        user = self.context.get("user")
        password = self.validated_data.get("password")
        user.set_password(password)
        user.save()
        return user


class GoogleAuthSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ["email", "name"]

    def validate(self, attrs):
        user_data = self.context.get("userdata")
        password = User.objects.make_random_password()
        user_data["password"] = password
        return user_data

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)


# Serializer for updating the new password
class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        fields = ["password", "password2"]


# serializers.py
class UserProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['image']
