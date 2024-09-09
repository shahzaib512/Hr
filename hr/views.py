# views.py
from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Organisation, Job, Application, OrganisationStaff
from .serializers import UserSerializer, OrganisationSerializer, JobSerializer, ApplicationSerializer, OrganisationStaffSerializer
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache


class RegisterUserView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


# Custom pagination class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# Custom permission class
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('organisation')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Updated to handle authenticated users
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'username']
    ordering_fields = ['created_at', 'updated_at']
    pagination_class = StandardResultsSetPagination

class OrganisationViewSet(viewsets.ModelViewSet):
    queryset = Organisation.objects.all().select_related('admin')
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Updated to handle authenticated users
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'location']
    ordering_fields = ['created_at', 'updated_at']
    pagination_class = StandardResultsSetPagination

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().select_related('organisation', 'created_by')
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Updated to handle authenticated users
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organisation', 'is_open']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at']
    pagination_class = StandardResultsSetPagination

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all().select_related('job', 'applicant')
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Updated to handle authenticated users
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'job']
    search_fields = ['skill_description', 'applicant__email']
    ordering_fields = ['created_at', 'updated_at']
    pagination_class = StandardResultsSetPagination


    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        application = self.get_object()
        status = request.data.get('status')
        if status:
            application.status = status
            application.save()
            return Response({'status': status}, status=status.HTTP_200_OK)
        return Response({'error': 'Status not provided'}, status=status.HTTP_400_BAD_REQUEST)


class OrganisationStaffViewSet(viewsets.ModelViewSet):
    queryset = OrganisationStaff.objects.all().select_related('organisation', 'user')
    serializer_class = OrganisationStaffSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Updated to handle authenticated users
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'organisation__name']
    ordering_fields = ['created_at', 'updated_at']
    pagination_class = StandardResultsSetPagination




    def send_application_notification(user_email, job_title):
        subject = 'Application Received'
        message = f'Your application for the job {job_title} has been received.'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])


    def get_cached_job_list():
        jobs = cache.get('job_list')
        if not jobs:
            jobs = list(Job.objects.all())
            cache.set('job_list', jobs, timeout=60*15)
        return jobs
