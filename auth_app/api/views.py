from django.core.mail import send_mail

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

User = get_user_model() 


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            # Die save()-Methode des Serializers ruft jetzt die create()-Methode auf,
            # die den Benutzer als inaktiv speichert.
            saved_account = serializer.save()
            uid = urlsafe_base64_encode(force_bytes(saved_account.pk))
            token = default_token_generator.make_token(saved_account)
            # Stelle sicher, dass dies die korrekte URL zu deiner Aktivierungs-View ist
            activation_link = f"http://localhost:8000/api/activate/{uid}/{token}/" 

            

            subject = 'Willkommen bei Videoflix 🎬 – Aktiviere deinen Account'
            text_content = f'Danke für deine Registrierung, {saved_account.username}!\n\nKlicke auf den folgenden Link, um deinen Account zu aktivieren:\n\n{activation_link}'
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
            
            # WICHTIG: Hier gibst du einen Token zurück. Der Benutzer ist aber noch inaktiv.
            # Wenn du nicht möchtest, dass ein Token zurückgegeben wird, solange der Benutzer inaktiv ist,
            # könntest du diesen Teil weglassen oder eine andere Meldung senden.
            # Für die meisten Anwendungsfälle ist es jedoch in Ordnung, da der Token beim Login nicht gültig ist.
            refresh = RefreshToken.for_user(saved_account)
            data = {
                'user': {
                    'id': saved_account.pk,
                    'email': saved_account.email,
                    #'is_active': saved_account.is_active # Füge is_active zur Response hinzu
                },
                'token': str(refresh.access_token)
            }
            return Response(data, status=status.HTTP_201_CREATED) # Verwende HTTP_201_CREATED für erfolgreiche Erstellung
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class HelloWorldView(APIView):
    # Ändere die Signatur der get-Methode
    def get(self, request, uidb64, token):
        try:
            # uidb64 entschlüsseln, um die User-ID zu erhalten
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            # Token ist gültig, aktiviere den Benutzer
            user.is_active = True
            user.save()
            return Response({"message": "Account activated successfully!"}, status=status.HTTP_200_OK)
        else:
            # Token ist ungültig oder der Benutzer existiert nicht
            return Response({"message": "Activation link is invalid or has expired!"}, status=status.HTTP_400_BAD_REQUEST)


# from django.views.generic import TemplateView

# class HelloWorldView(TemplateView):
#     template_name = "registration_success.html"
    
# ... (deine anderen Views CookieTokenObtainPairView, CookieTokenRefreshView, ActivateUserView bleiben wie sie sind,
# mit der oben genannten Anpassung im CustomTokenObtainPairSerializer)

# class CookieTokenObtainPairView(TokenObtainPairView):
    
#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         refresh = response.data.get("refresh")
#         access = response.data.get("access")

#         response.set_cookie(
#             key="access_token",
#             value=access,
#             httponly=True,
#             secure=True,
#             samesite="Lax"
#         )

#         response.set_cookie(
#             key="refresh_token",
#             value=refresh,
#             httponly=True,
#             secure=True,
#             samesite="Lax"
#         )

#         response.data = {"message": "login successfully"}
#         return response

# ---------------wird benutzt wenn die Cookies auf die Email umgestellt werden ---------------
class CookieTokenObtainPairView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
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
    
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except:
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
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return Response({'detail': 'Ungültiger Link'}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'detail': 'Konto erfolgreich aktiviert'})
        else:
            return Response({'detail': 'Ungültiger oder abgelaufener Token'}, status=400)

class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        
        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found in cookies."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or already blacklisted token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = Response({
            "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
        }, status=status.HTTP_200_OK)

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        
        return response
    

class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
           
            return Response({"detail": "An email has been sent to reset your password."}, status=status.HTTP_204_NO_CONTENT)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://localhost:8000/api/password_reset_confirm/{uid}/{token}/"

        subject = 'Passwort zurücksetzen – Videoflix'
        text_content = f'Hallo {user.username},\n\nKlicke auf den folgenden Link, um dein Passwort zurückzusetzen:\n\n{reset_link}'
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
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
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