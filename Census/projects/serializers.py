from rest_framework import serializers
from .models import *

# Serializer for Categories
class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['name']


# Serializer for Technologies
class TechnologiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technologies
        fields = ['name', 'popularity']

# Serializer for Authors
class AuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authors
        fields = '__all__'
        extra_kwargs = {
            'slug': {'required': False},
            'email': {'required': False},
            'linkedin_url': {'required': False},
            'github_url': {'required': False},
            'linkedin_url': {'required': False},
            'avatar_url': {'required': False},
            'bio_url': {'required': False},
            'role': {'required': False},
            'bio': {'required': False},
        }


# Serializer for Updates
class UpdatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Updates
        fields = '__all__'

# Serializer for Submissions
class SubmissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submissions
        fields = '__all__'

# Serializer for ProjectCategory
class ProjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = '__all__'


# Serializer for ProjectTechnology
class ProjectTechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTechnology
        fields = '__all__'


# Serializer for ProjectAuthor
class ProjectAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAuthor
        fields = '__all__'


# Serializer for Projects
class ProjectsSerializer(serializers.ModelSerializer):

    categories = CategoriesSerializer(required=False, many=True, read_only=True)
    technologies = TechnologiesSerializer(required=False, many=True, read_only=True)
    authors = AuthorsSerializer(many=True, read_only=True)
    class Meta:
        model = Projects
        fields = '__all__'
        extra_kwargs = {
            'logo_url': {'required': False},
            'cover_url': {'required': False},
            'description': {'required': False},
            'short_description': {'required': False},
            'stage': {'required': False},
            'needs': {'required': False},
            'email': {'required': False},
            'website_url': {'required': False},
            'github_url': {'required': False},
            'twitter_url': {'required': False},
            'city':{'required': False},
            'address':{'required': False},
            'latitude': {'required': False},
            'longitude': {'required': False},
            'founded_date': {'required': False},
        }
    