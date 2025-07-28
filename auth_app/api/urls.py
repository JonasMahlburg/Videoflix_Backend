from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path, include
from .views import RegistrationView, CookieTokenObtainPairView, CookieTokenRefreshView

urlpatterns = [
    # path('registration/', RegistrationView.as_view(), name='registration'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]