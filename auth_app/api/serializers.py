from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles the creation of a new, inactive user account, validates email
    uniqueness, and ensures that the password and confirmed password match.
    """
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

    def create(self, validated_data):
        """
        Creates and returns a new user instance, setting `is_active` to False.

        Args:
            validated_data (dict): The validated data from the serializer.

        Returns:
            User: The newly created, inactive user instance.
        """
        email = validated_data['email']
        password = validated_data['password']
        
        # Der Username wird hier aus der E-Mail generiert, aber die Validierung
        # findet in der `validate`-Methode statt.
        username = email.split('@')[0]

        user = User.objects.create_user(
            email=email,
            username=username,
            password=password
        )
        user.is_active = False
        user.save()
        return user

    def validate_confirmed_password(self, value):
        """
        Validates that the password and confirmed password fields match.

        Args:
            value (str): The value of the confirmed_password field.

        Returns:
            str: The confirmed_password value if valid.

        Raises:
            serializers.ValidationError: If the passwords do not match.
        """
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value

    def validate_email(self, value):
        """
        Validates that the email does not already exist in the database (case-insensitive).

        Args:
            value (str): The value of the email field.

        Returns:
            str: The email value if it is unique.

        Raises:
            serializers.ValidationError: If a user with the email already exists.
        """
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def validate(self, data):
        """
        Performs object-level validation, including checking for duplicate usernames.
        """
        email = data.get('email')
        if email:
            username = email.split('@')[0]
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError('A user with this username already exists.')
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for obtaining JWT tokens using email instead of username.

    This serializer validates user credentials (email and password), checks
    if the account is active, and returns a valid token pair if successful.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        """
        Initializes the serializer and removes the default username field.
        """
        super().__init__(*args, **kwargs)

        if "username" in self.fields:
            self.fields.pop("username")

    def validate(self, attrs):
        """
        Validates the user's email and password.

        This method overrides the default validation to use email for
        authentication and checks the `is_active` status of the user.

        Args:
            attrs (dict): A dictionary of the fields to validate.

        Returns:
            dict: The validated data, including the access and refresh tokens.

        Raises:
            serializers.ValidationError: If the email/password is invalid or
                                         the account is not active.
        """
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid password or email!")

        if not user.is_active:
            raise serializers.ValidationError(
                "Account not active. Please check your email for activation link."
            )

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password or email!")

        data = super().validate({"username": user.username, "password": password})
        data['user'] = user
        return data