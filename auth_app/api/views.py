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

            send_mail(
                subject='Aktiviere deinen Account bei Videoflix!',
                message=f'Bitte klicke auf diesen Link zur Aktivierung: {activation_link}',
                from_email=None, # Hier solltest du einen FROM_EMAIL in deinen Django-Einstellungen definieren.
                recipient_list=[saved_account.email],
                fail_silently=False,
            )
            
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
        
        serializer= self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
    
        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]

        response = Response({"message": "Login successfully"})

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

        response.data = {"message": "login successfully"}
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

        response = Response({"message":"access Token refreshed"})
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