from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path, include
from .views import RegistrationView, CookieTokenObtainPairView, CookieTokenRefreshView

from .views import ActivateUserView, HelloWorldView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('activate/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate'),
    path('activate/<uidb64>/<token>/', HelloWorldView.as_view(), name='activate'),
]