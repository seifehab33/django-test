from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    location_list, camera_list, person_list, community_list, users_in_community_list, person_detail,
    camera_history_list, security_personnel_list, admin_list, login_person, login_admin,
    add_camera_history, add_security_personnel, add_admin, create_community,
    add_user_to_community, add_person, users_in_community_by_id, remove_user_from_community, edit_person_detail,
    get_counts, admin_login_history, camera_history_for_person, check_community_id, admin_image_view, person_image_view, delete_community, delete_person, delete_community_admin, admin_details, user_communities_No, edit_admin_detail, contact_view
)

urlpatterns = [
    path('Login/User/', login_person, name='Login-user'),
    path('Login/Admin/', login_admin, name='Login-Admin'),
    path('locations/', location_list, name='location-list'),
    path('cameras/', camera_list, name='camera-list'),
    path('persons/', person_list, name='person-list'),
    path('Signup/', add_person, name='add-person'),
    path('persons/<int:pk>/', person_detail, name='person-detail'),
    path('person/<int:pk>/image/', person_image_view, name='person_image'),
    path('communities/', community_list, name='community-list'),
    path('communities/create/', create_community, name='create-community'),
    path('communities/check/', check_community_id, name='create-community'),
    path('community/delete/<int:community_id>/',
         delete_community, name='community-delete'),
    path('delete-community/', delete_community_admin, name='delete_community'),


    path('users-in-community/', users_in_community_list,
         name='users-in-community-list'),
    path('add-user-to-community/', add_user_to_community,
         name='add-user-to-community'),
    path('remove-user-from-community/', remove_user_from_community,
         name='remove_user_from_community'),
    path('user/<int:user_id>/communities/',
         user_communities_No, name='user_communities'),

    path('person/<int:pk>/edit/', edit_person_detail, name='edit_person_detail'),
    path('person/<int:pk>/', delete_person, name='delete_person'),

    path('get_counts/', get_counts, name='get_counts'),

    path('users-in-community/<int:community_id>/',
         users_in_community_by_id, name='users_in_community_by_id'),
    path('camera-history/', camera_history_list, name='camera-history-list'),
    path('camera-history/<int:person_id>/',
         camera_history_for_person, name='camera_history_for_person'),
    path('security-personnels/', security_personnel_list,
         name='security-personnel-list'),
    path('admins/', admin_list, name='admin-list'),
    path('admins/login/history/<int:admin_id>/',
         admin_login_history, name='admin_login_history'),
    path('admin-edit/<int:pk>/', edit_admin_detail, name='edit_admin_detail'),

    path('camera-history/add/', add_camera_history, name='add_camera_history'),
    path('security-personnel/add/', add_security_personnel,
         name='add_security_personnel'),
    path('admin/add/', add_admin, name='add_admin'),
    path('admin-details/<int:admin_id>/', admin_details, name='admin_details'),

    path('admin-image/<int:admin_id>/', admin_image_view, name='admin-image'),
    path('contact/', contact_view, name='contact_view'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
