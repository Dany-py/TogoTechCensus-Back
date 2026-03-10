from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from .serializers import ProjectsSerializer, CategoriesSerializer, TechnologiesSerializer, AuthorsSerializer, AudiencesSerializer
from .models import Projects, Categories, Technologies, Authors
from .permissions import IsOwnerOrReadOnly
from rest_framework.pagination import PageNumberPagination

class ProjectPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# View for the Projects model
class ProjectView(APIView):
    #permission_classes= [permissions.IsAuthenticated]
    def get(self, request):
        projects = Projects.objects.all().order_by('created_at')
        paginator = ProjectPagination()
        page = paginator.paginate_queryset(projects, request)
        
        if page is not None:
            serializer = ProjectsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ProjectsSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProjectsSerializer(data=request.data)
        parser_classes = (MultiPartParser, JSONParser)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View for the Categories model
class CategorieView(APIView):

    permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    def get(self, request):
        categorie = Categories.objects.all()
        serializer = CategoriesSerializer(categorie, many=True)
        return Response(serializer.data)

# View for the Technologies model
class TechnologieView(APIView):

    permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    def get(self, request):
        techno = Technologies.objects.all()
        serializer = TechnologiesSerializer(techno, many=True)
        return Response(serializer.data)

# View for the Author model
class AuthorView(APIView):

    permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    def get(self, request):
        authors = Authors.objects.all()
        serializer = AuthorsSerializer(authors, many=True)
        return Response(serializer.data)
