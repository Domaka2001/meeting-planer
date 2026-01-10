from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_meeting, name='create_meeting'),
    path('meeting/<uuid:meeting_id>/success/', views.meeting_success, name='meeting_success'),
    path('meeting/<uuid:meeting_id>/delete/', views.delete_meeting, name='delete_meeting'),
    path('meeting/<uuid:meeting_id>/', views.meeting_vote, name='meeting_vote'),
    path('meeting/<uuid:meeting_id>/vote/', views.submit_vote, name='submit_vote'),
    path('meeting/<uuid:meeting_id>/results/', views.meeting_results, name='meeting_results'),
    path('htmx/add-timeslot/', views.add_timeslot_field, name='add_timeslot_field'),
    path('htmx/add-location/', views.add_location_field, name='add_location_field'),
]
