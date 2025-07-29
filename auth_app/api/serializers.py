from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }
    # Beispiel im Serializer
    # def create(self, validated_data):
    #     user = User.objects.create_user(**validated_data)
    #     user.is_active = False
    #     user.save()
    #     return user
    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        # username wird benötigt, da AbstractUser einen username erwartet.
        # Du kannst dies nach Belieben anpassen (z.B. user = User.objects.create_user(email=email, password=password))
        # wenn du ein Custom User Model hast, das keinen username erfordert.
        user = User.objects.create_user(
            email=email,
            username=email.split('@')[0], # Oder einen anderen Standard-Username
            password=password
        )
        user.is_active = False # Hier wird der Benutzer inaktiv gesetzt
        user.save()
        return user

    def validate_confirmed_password(self, value):
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    # def save(self):
    #     pw = self.validated_data['password']

    #     account = User(email=self.validated_data['email'], username=self.validated_data['email'].split('@')[0])
    #     account.set_password(pw)
    #     account.save()
    #     return account
    
#----------für Cookies über Email ----------------


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

   #----------nimmt username aus der validation raus, so dass dann email benutzt werden kann------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "username"in self.fields:
            self.fields.pop("username")

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try: 
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid password or email!")
        
        if not user.is_active:
            raise serializers.ValidationError("Account not active. Please check your email for activation link.")
        
        
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password or email!")
        
        data = super().validate({"username": user.username, "password": password})
        return data