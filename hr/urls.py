# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, OrganisationViewSet, JobViewSet, ApplicationViewSet, OrganisationStaffViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'organisations', OrganisationViewSet)
router.register(r'jobs', JobViewSet)
router.register(r'applications', ApplicationViewSet)
router.register(r'organisation-staff', OrganisationStaffViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
