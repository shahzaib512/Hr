# serializers.py
from rest_framework import serializers
from .models import User, Organisation, Job, Application, OrganisationStaff


class OrganisationSerializer(serializers.ModelSerializer):
    admin_email = serializers.ReadOnlyField(source='admin.email')

    class Meta:
        model = Organisation
        fields = ['id', 'name', 'valuation', 'location', 'admin', 'admin_email', 'staff_access_code', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    organisation_details = OrganisationSerializer(source='organisation', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'organisation', 'organisation_details', 'is_active', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Create a user with hashed password
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        # Update user details
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class JobSerializer(serializers.ModelSerializer):
    organisation_name = serializers.ReadOnlyField(source='organisation.name')
    created_by_email = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Job
        fields = ['id', 'created_by', 'created_by_email', 'organisation', 'organisation_name', 'title', 'description', 'is_open', 'created_at', 'updated_at']


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'job', 'applicant', 'skill_description', 'status', 'created_at', 'updated_at']

    def validate_skill_description(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Skill description is too short.")
        return value



class OrganisationStaffSerializer(serializers.ModelSerializer):
    organisation_name = serializers.ReadOnlyField(source='organisation.name')
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = OrganisationStaff
        fields = ['id', 'organisation', 'organisation_name', 'user', 'user_email', 'role', 'created_at', 'updated_at']
