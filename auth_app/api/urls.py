
from django.urls import path
from .views import(RegistrationView,
                    CookieTokenObtainPairView, 
                    CookieTokenRefreshView,
                    HelloWorldView, 
                    LogoutView,
                    PasswordResetView,
                    PasswordResetConfirmView,
                    ) 
 

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('activate/<uidb64>/<token>/', HelloWorldView.as_view(), name='activate'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_confirm'),
]