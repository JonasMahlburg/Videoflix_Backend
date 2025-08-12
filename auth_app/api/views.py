import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class RegistrationView(APIView):
    """
    Handles user registration.

    This view creates a new inactive user account and sends an activation email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Creates a new user account and sends an activation email.

        Args:
            request (Request): The incoming request.

        Returns:
            Response: A response with user data and a token if registration is
                      successful (HTTP 201), or serializer errors (HTTP 400).
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            uid = urlsafe_base64_encode(force_bytes(saved_account.pk))
            token = default_token_generator.make_token(saved_account)
            activation_link = f"http://127.0.0.1:5500/pages/auth/activate.html?uid={uid}&token={token}"

            subject = 'Welcome to Videoflix 🎬 – Activate Your Account'
            text_content = (f'Thanks for registering, {saved_account.username}!\n\n'
                            f'Click the following link to activate your account:\n\n'
                            f'{activation_link}')
            html_content = render_to_string('emails/activation_email.html', {
                'username': saved_account.username,
                'activation_link': activation_link
            })

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email='Videoflix <noreply@jonas-mahlburg.de>',
                to=[saved_account.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            refresh = RefreshToken.for_user(saved_account)
            data = {
                'user': {
                    'id': saved_account.pk,
                    'email': saved_account.email,
                },
                'token': str(refresh.access_token)
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HelloWorldView(APIView):
    """
    A temporary view to test account activation.
    
    This view is responsible for activating a user account using a uid and token.
    """
    def get(self, request, uidb64, token):
        """
        Activates a user account based on the provided UID and token.

        Args:
            request (Request): The incoming request.
            uidb64 (str): The base64-encoded user ID.
            token (str): The activation token.

        Returns:
            Response: A success message if activation is successful (HTTP 200),
                      or an error message if the link is invalid (HTTP 400).
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account activated successfully!"}, status=status.HTTP_200_OK)
        return Response({"message": "Activation link is invalid or has expired!"}, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining JWT tokens and setting them as HTTP-only cookies.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        Handles user login, creates JWT tokens, and sets them in cookies.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]

        response = Response({
            "detail": "Login successful",
            "user": {
                "id": serializer.user.id,
                "username": serializer.user.username
            }
        })

        response.set_cookie(
            key="access_token",
            value=str(access),
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Custom view for refreshing JWT access tokens using a refresh token from cookies.
    """
    def post(self, request, *args, **kwargs):
        """
        Refreshes the access token using a refresh token from the request cookies.
        """
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Refresh token invalid: {e}")
            return Response(
                {"detail": "Refresh token invalid!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        access_token = serializer.validated_data.get("access")

        response = Response({
            "detail": "Token refreshed",
            "access": access_token
        })
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        return response


class ActivateUserView(APIView):
    """
    View for user account activation.
    
    This view is a simplified, cleaner version of HelloWorldView for production use.
    """
    def get(self, request, uidb64, token):
        """
        Activates a user account.
        
        Args:
            request (Request): The incoming request.
            uidb64 (str): The base64-encoded user ID.
            token (str): The activation token.
            
        Returns:
            Response: A success or error response.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return Response({'detail': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'detail': 'Account successfully activated'})
        return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Handles user logout by blacklisting the refresh token and deleting cookies.
    """
    def post(self, request):
        """
        Blacklists the refresh token and clears the access and refresh token cookies.
        """
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found in cookies."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            logger.error(f"Failed to blacklist refresh token: {e}")
            return Response(
                {"detail": "Invalid or already blacklisted token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = Response({
            "detail": "Logged out successfully! All tokens have been cleared."
        }, status=status.HTTP_200_OK)

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class PasswordResetView(APIView):
    """
    Initiates the password reset process by sending a reset email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Sends a password reset email to the user.
        
        If the email is not found, a 204 response is returned to prevent
        email enumeration attacks.
        """
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "An email has been sent to reset your password."},
                status=status.HTTP_204_NO_CONTENT
            )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://127.0.0.1:5500/pages/auth/confirm_password.html?uid={uid}&token={token}"

        subject = 'Password Reset – Videoflix'
        text_content = (f'Hello {user.username},\n\n'
                        f'Click the following link to reset your password:\n\n'
                        f'{reset_link}')
        html_content = render_to_string('emails/password_reset_email.html', {
            'username': user.username,
            'reset_link': reset_link
        })

        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email='Videoflix <noreply@jonas-mahlburg.de>',
            to=[user.email]
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()

        return Response({"detail": "An email has been sent to reset your password."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Confirms the password reset and sets a new password.
    """
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """
        Validates the password reset token and sets a new password for the user.
        
        Args:
            request (Request): The incoming request with new password data.
            uidb64 (str): The base64-encoded user ID.
            token (str): The password reset token.
            
        Returns:
            Response: A success or error response.
        """
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not new_password or not confirm_password:
            return Response({"detail": "Both password fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Your Password has been successfully reset."}, status=status.HTTP_200_OK)