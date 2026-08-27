from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from django.utils.text import slugify
from django.db.models import Count, Sum, F
from django.db import transaction
from .serializers import ProjectsSerializer, CategoriesSerializer, TechnologiesSerializer, AuthorsSerializer
from .models import Projects, Categories, Technologies, Authors
from .permissions import IsOwnerOrReadOnly
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import SessionAuthentication

class ProjectPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 100

# View for the Projects model

class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

class UnAuthenticateProjectView(APIView):
    
    def get(self, request):
        projects = Projects.objects.filter(is_verified=True).order_by('created_at')
    
        name = request.query_params.get('name')
        type = request.query_params.get('type')
        author = request.query_params.get('author')
        categorie = request.query_params.get('category')
        technologie = request.query_params.get('technology')

        if name:
            slug = slugify(name)
            project = projects.filter(slug__icontains=slug)

            serializer = ProjectsSerializer(project, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        if type:
            slug = slugify(type)
            project = projects.filter(type__icontains=slug)

            paginator = ProjectPagination()
            page = paginator.paginate_queryset(project, request)
        
            if page is not None:
                serializer = ProjectsSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        
            serializer = ProjectsSerializer(project, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        if author:
            slug = slugify(author)
            project = projects.filter(authors__name__icontains=slug)

            paginator = ProjectPagination()
            page = paginator.paginate_queryset(project, request)
        
            if page is not None:
                serializer = ProjectsSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        
            serializer = ProjectsSerializer(project, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        if categorie:
            slug = slugify(categorie)
            project = projects.filter(categories__name__icontains=slug)

            paginator = ProjectPagination()
            page = paginator.paginate_queryset(project, request)
        
            if page is not None:
                serializer = ProjectsSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        
            serializer = ProjectsSerializer(project, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        if technologie:
            slug = slugify(technologie)
            project = projects.filter(technologies__name__icontains=slug)

            paginator = ProjectPagination()
            page = paginator.paginate_queryset(project, request)
        
            if page is not None:
                serializer = ProjectsSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        
            serializer = ProjectsSerializer(project, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        paginator = ProjectPagination()
        unsafeprojects = Projects.objects.filter(is_verified=True).exclude(type='open-source').order_by('created_at')
        page = paginator.paginate_queryset(unsafeprojects, request)
        
        if page is not None:
            serializer = ProjectsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ProjectsSerializer(project, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProjectView(APIView):

    def get_permissions(self):
        try:
            if self.request.method == 'POST':
                return [permissions.IsAuthenticated()]
        
            if self.request.method == 'GET' or self.request.method == 'PATCH':
                return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        
            return []
        except Exception as e:
            print(f"\n❌ Erreur dans get_permissions : {e}")
            return []

    def get(self, request):
        projects = Projects.objects.all().order_by('created_at')            

        if request.query_params.get('filter') == 'mine':
            project = projects.filter(user=request.user, is_verified=True) 
            paginator = ProjectPagination()
            page = paginator.paginate_queryset(project, request)
        
            if page is not None:
                serializer = ProjectsSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        
            serializer = ProjectsSerializer(project, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        paginator = ProjectPagination()
        page = paginator.paginate_queryset(projects, request)
        
        if page is not None:
            serializer = ProjectsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ProjectsSerializer(project, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        user = request.user
    
        if not user.is_authenticated:
            return Response(
                {"error": "User matching query does not exist."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            serializer = ProjectsSerializer(data=request.data)
            
            authors_data = request.data.get('authors', '')
            authors = authors_data.split(', ') if authors_data else [user.name]
            
            technologies = request.data.get('technologies', '')
            
            categories = request.data.get('categories', '')
            
            with transaction.atomic():
                if serializer.is_valid():
                    project = serializer.save(user=user)
                    
                    if authors:
                        for author in authors:
                            author_data = {
                                'name':author,
                                'slug': slugify(author),
                                'role': 'project-leader'
                            }
                            authors_serializer = AuthorsSerializer(data=author_data)
                            if  authors_serializer.is_valid():
                                author_obj = authors_serializer.save()
                                project.authors.add(author_obj)
                            else:
                                raise ValueError(f"Author invalide : {authors_serializer.errors}")
                            
                    if categories:
                        category_id = Categories.objects.filter(name=categories).values_list('id', flat=True).first()
                        project.categories.add(category_id)
                    else:
                        raise ValueError("Category field required !")
                         
                    if technologies:
                        for techno in technologies:
                            tech_slug = Technologies.objects.filter(slug=slugify(techno))
                            tech_id = Technologies.objects.filter(slug=slugify(techno)).values_list('id', flat=True).first()                    
                            if tech_slug:
                                project.technologies.add(tech_id)
                                pass
                            else:
                                techno_data = {
                                    'name': techno,
                                    'slug': slugify(techno)
                                }
                                techno_serializer = TechnologiesSerializer(data=techno_data)
                                if techno_serializer.is_valid():
                                    techno_obj = techno_serializer.save()
                                    project.technologies.add(techno_obj)
                                else:
                                    raise ValueError(f"Techno invalide : {techno_serializer.errors}")
                    else:
                        raise ValueError("Technology field required !")
                        
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
        
                print(f'\nSerializer errors :', serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"\n❌ Post View Error : {e}")
            return Response({"detail": "Une erreur est survenue."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def patch(self, request, id):
        #id = request.query_params.get('id')
        user = request.user
    
        if not user.is_authenticated:
            return Response(
                {"error": "User matching query does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = Projects.objects.get(id=id)
            if project.user != user:
                return Response(
                    {"error": "You don't have permission to modify this project."},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = ProjectsSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response(serializer.data, status=status.HTTP_200_OK)
        
            print(f'\nSerializer errors:', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Projects.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"\n❌ Erreur {e}")
            return Response({"detail": "Une erreur est survenue."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProjectStats(APIView):
    
    def get_permissions(self):
        try:        
            if self.request.method == 'GET':
                return [permissions.IsAuthenticated()]
            return []
        except Exception as e:
            print(f"\n❌ Erreur dans get_permissions : {e}")
            return []
        
    def patch(self, request, id):
        try:
            updated = Projects.objects.filter(pk=id).update(view_count=F('view_count') + 1)
            if not updated:
                return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": "View count updated"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"\n❌ Erreur {e}")
            return Response({"detail": "Une erreur est survenue."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get(self, request):
        
        param = request.query_params.get('project')
        filter_param= request.query_params.get('filter')
        projects = Projects.objects.all()
        authors = Authors.objects.all()
        
        try:

            if param == 'featured':
                featured = projects.filter(artificial_view__gte=100)
                paginator = ProjectPagination()
                page = paginator.paginate_queryset(featured, request)        
                if page is not None:
                    serializer = ProjectsSerializer(page, many=True)
                    return paginator.get_paginated_response(serializer.data)
            
            if filter_param == 'mine':
                user_has_project = True if len(projects.filter(user=request.user)) > 0 else False
                if user_has_project:
                    view_count = projects.filter(user=request.user, is_verified=True).aggregate(view= Sum('view_count'))
                    artificial_view = projects.filter(user=request.user, is_verified=True).aggregate(view=Sum('artificial_view'))
                    active = projects.filter(user=request.user, is_verified=True).aggregate(total_active=Count('id'))
                    user_project = projects.filter(user=request.user).aggregate(total_active=Count('id'))                
                    view_field = 'view_count' if view_count.get('view') > artificial_view.get('view') else 'artificial_view'
                    view = projects.filter(user=request.user, is_verified=True).aggregate(total_view=Sum(view_field))
                    pub_rate = round((active.get('total_active')/user_project.get('total_active')*100), 2)                
                    user_stats = {
                        'active': active.get('total_active'),
                        'view': view.get('total_view'),
                        'rate': pub_rate
                    }
                    return Response(user_stats)
                
                user_stats = {
                        'active': 0,
                        'view': 0,
                        'rate': 0
                    }
                return Response(user_stats)
             
            startup = projects.filter(type='startup', is_verified=True).aggregate(
                total_startup=Count('id')
            )
            open_source = projects.filter(type='open-source', is_verified=True).aggregate(
                total_open_source=Count('id')
            )
            developper = authors.filter(role__icontains='developper').aggregate(
                total_developper = Count('id')
            )        
            new_projects = projects.filter(is_verified=True).aggregate(
                total_new_projects=Count('id')
            )

            stats = {
                'startup': startup.get('total_startup'),
                'open_source': open_source.get('total_open_source'),
                'developper': developper.get('total_developper'),
                'news': new_projects.get('total_new_projects')
            }

            return Response(stats)
        except Exception as e:
            print(f"\n❌ Error {e}")
            return Response({"detail": "Une erreur est survenue."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View for the Categories model
class CategoriesView(APIView):

    #permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    def get(self, request):
        categorie = Categories.objects.all()
        serializer = CategoriesSerializer(categorie, many=True)
        return Response(serializer.data)

# View for the Technologies model
class TechnologiesView(APIView):

    #permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    def get(self, request):
        techno = Technologies.objects.all()
        serializer = TechnologiesSerializer(techno, many=True)
        return Response(serializer.data)

# View for the Author model
class AuthorView(APIView):

    #permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    def get(self, request):
        authors = Authors.objects.all()
        serializer = AuthorsSerializer(authors, many=True)
        return Response(serializer.data)
