from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
    ForgotPasswordSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
from django.core.files.base import ContentFile
import requests as http_requests
from urllib.parse import urlparse
import os
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
import traceback
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str

def serialize_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "profile_image": (
            user.profile_image.url
            if user.profile_image
            else None
        ),
    }

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Register berhasil",
            "data": serializer.data
        }, status=201)
    return Response(serializer.errors, status=400)

@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == "GET":
        serializer = ProfileSerializer(request.user)
        return Response({
            "message": "Profile berhasil diambil",
            "data": serializer.data
        })
    serializer = ProfileSerializer(
        request.user,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        old_image = None
        if (
            "profile_image" in request.FILES
            and request.user.profile_image
        ):
            old_image = request.user.profile_image.path
        serializer.save()
        if old_image and os.path.isfile(old_image):
            try:
                os.remove(old_image)
            except Exception:
                pass
        return Response({
            "message": "Profile berhasil diperbarui",
            "data": serializer.data
        })
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    email = serializer.validated_data["email"]
    user = User.objects.filter(email=email).first()
    if not user:
        return Response({
            "message": "Jika email terdaftar, link reset password akan dikirim."
        })
    token_generator = PasswordResetTokenGenerator()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    reset_link = (
        f"http://localhost:3000/login/reset-password"
        f"?uid={uid}&token={token}"
    )
    subject = "Reset Password ShopAI"
    message = f"""
Halo {user.username},
Kami menerima permintaan untuk mereset password akun ShopAI Anda.
Silakan klik link berikut:
{reset_link}
Jika Anda tidak meminta reset password, abaikan email ini.
Terima kasih.
Tim ShopAI
"""
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
    return Response({
        "message": "Jika email terdaftar, link reset password telah dikirim."
    })

@api_view(["POST"])
def reset_password(request):
    uid = request.data.get("uid")
    token = request.data.get("token")
    password = request.data.get("password")

    if not uid or not token or not password:
        return Response(
            {
                "message": "Semua field wajib diisi"
            },
            status=400,
        )

    try:
        user_id = force_str(
            urlsafe_base64_decode(uid)
        )

        user = User.objects.get(pk=user_id)

    except Exception:
        return Response(
            {
                "message": "Link reset password tidak valid"
            },
            status=400,
        )

    if not default_token_generator.check_token(
        user,
        token,
    ):
        return Response(
            {
                "message": "Token sudah tidak berlaku"
            },
            status=400,
        )

    user.set_password(password)
    user.save()

    return Response(
        {
            "message": "Password berhasil diubah"
        }
    )


@api_view(["POST"])
def google_login(request):
    credential = request.data.get("credential")
    if not credential:
        return Response(
            {"message": "Credential wajib diisi"},
            status=400,
        )
    try:
        id_info = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        email = id_info["email"]
        name = id_info.get("name")
        picture = id_info.get("picture")
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {
                    "is_registered": False,
                    "credential": credential,
                    "email": email,
                    "name": name,
                    "picture": picture,
                },
                status=200,
            )
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "is_registered": True,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": serialize_user(user),
            }
        )
    except ValueError:
        return Response(
            {"message": "Google Token tidak valid"},
            status=400,
        )

@api_view(["POST"])
def google_register(request):
    credential = request.data.get("credential")
    role = request.data.get("role")
    if not credential or not role:
        return Response(
            {"message": "Credential dan role wajib diisi"},
            status=400,
        )
    if role not in ["buyer", "seller"]:
        return Response(
            {"message": "Role tidak valid"},
            status=400,
        )
    try:
        id_info = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        email = id_info["email"]
        if User.objects.filter(email=email).exists():
            return Response(
                {"message": "Email sudah terdaftar"},
                status=400,
            )
        username = email.split("@")[0]
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        user = User.objects.create_user(
            username=username,
            email=email,
            role=role,
        )
        picture = id_info.get("picture")
        if picture:
            image_response = http_requests.get(picture)
            if image_response.status_code == 200:
                extension = os.path.splitext(
                    urlparse(picture).path
                )[1]
                if not extension:
                    extension = ".jpg"
                filename = f"{username}{extension}"
                user.profile_image.save(
                    filename,
                    ContentFile(image_response.content),
                    save=True,
                )
        user.set_unusable_password()
        user.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": serialize_user(user),
            },
            status=201,
        )
    except Exception:
        traceback.print_exc()
        return Response(
            {
                "message": "Register Google gagal"
            },
            status=400,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
