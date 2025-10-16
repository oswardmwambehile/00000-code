import re
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User
from rest_framework import serializers
from .models import Branch

class UserRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "contact",
            "password1",
            "password2",
            "company_name",
            "position",
            "zone",
            "branch",
        )
        extra_kwargs = {"email": {"required": True}}

    def validate_contact(self, value):
        # Tanzanian phone number validation
        pattern = r'^(?:\+255|0)[67][0-9]{8}$'
        if value and not re.match(pattern, value):
            raise serializers.ValidationError(
                "Enter a valid Tanzanian phone number (e.g. +255712345678 or 0712345678)"
            )
        return value

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match!"})
        validate_password(attrs["password1"])
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password1")
        validated_data.pop("password2")
        user = User.objects.create_user(password=password, **validated_data)
        return user


# --------------------------
# User Login Serializer
# --------------------------
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data.get("email"), password=data.get("password"))
        if not user:
            raise serializers.ValidationError(
                "Invalid credentials or inactive account."
            )
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        return user


# --------------------------
# General User Serializer (for JWT responses, user info)
# --------------------------
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "contact",
            "company_name",
            "position",
            "zone",
            "branch",
        )
        read_only_fields = ("id", "email")


# --------------------------
# User Profile Serializer
# --------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "contact",
            "company_name",
            "position",
            "zone",
            "branch",
        )


# --------------------------
# Update Profile Serializer
# --------------------------
class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "contact",
            "company_name",
            "position",
            "zone",
            "branch",
        )

    def validate_contact(self, value):
        pattern = r'^(?:\+255|0)[67][0-9]{8}$'
        if value and not re.match(pattern, value):
            raise serializers.ValidationError(
                "Enter a valid Tanzanian phone number."
            )
        return value


# --------------------------
# Change Password Serializer
# --------------------------
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])





class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_name(self, value):
       
        branch_id = self.instance.id if self.instance else None

        if Branch.objects.exclude(id=branch_id).filter(name__iexact=value).exists():
            raise serializers.ValidationError("A branch with this name already exists.")
        
        return value


from rest_framework import serializers
from .models import User

class UserListSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'company_name', 'position', 'zone', 'branch_name',
            'contact', 'is_active', 'date_joined'
        ]



class UserDetailSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = User
        fields = '__all__'



class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'company_name',
            'position', 'zone', 'branch', 'contact', 'is_active'
        ]


