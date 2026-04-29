from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),

    # Event pages
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('event/<int:pk>/register/', views.register, name='register'),
    path('event/<int:pk>/updates/', views.live_updates, name='live_updates'),
    path('event/<int:pk>/post-update/', views.post_update, name='post_update'),

    # Registration success
    path('register/success/<uuid:token>/', views.register_success, name='register_success'),

    # Admin dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Admin actions
    path('attendance/<int:pk>/toggle/', views.toggle_attendance, name='toggle_attendance'),
    path('transaction/<int:pk>/verify/', views.verify_transaction, name='verify_transaction'),
    path('schedule/<int:pk>/current/', views.mark_schedule_current, name='mark_schedule_current'),

    # Feedback & certificate
    path('feedback/<uuid:token>/', views.submit_feedback, name='submit_feedback'),
    path('certificate/<uuid:token>/', views.certificate, name='certificate'),

    # API
    path('api/stats/', views.api_stats, name='api_stats'),
]