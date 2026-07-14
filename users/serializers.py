from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "role",
            "profile_image",
        ]
        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username sudah digunakan"
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email sudah digunakan"
            )
        return value

    def create(self, validated_data):
        profile_image = validated_data.pop("profile_image", None)
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data["role"],
        )
        if profile_image:
            user.profile_image = profile_image
            user.save()
        return user
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "role": self.user.role,
            "profile_image": (
                self.user.profile_image.url
                if self.user.profile_image
                else None
            ),
        }
        return data
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "profile_image",
        ]
        read_only_fields = [
            "email",
            "role",
        ]
    def validate_username(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError(
                "Username sudah digunakan."
            )
        return value

    def validate_profile_image(self, value):
        if value:
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError(
                    "Ukuran gambar maksimal 2 MB."
                )
            allowed_types = [
                "image/jpeg",
                "image/png",
                "image/jpg",
                "image/webp",
            ]
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "Format gambar harus JPG, JPEG, PNG atau WEBP."
                )
        return value

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()