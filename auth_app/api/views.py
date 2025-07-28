from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            refresh = RefreshToken.for_user(saved_account)
            data = {
                'user': {
                    'id': saved_account.pk,
                    'email': saved_account.email
                },
                'token': str(refresh.access_token)
            }
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class HelloWorldView(APIView):
    permission_classes= [IsAuthenticated]

    def get(self, request):
        return Response({'message':'Hello World'})
    

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