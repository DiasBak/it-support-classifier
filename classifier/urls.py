from django.urls import path
from . import views

urlpatterns = [

    path('', views.index),
    path('dashboard/', views.dashboard),
    path('classify/', views.classify),
    path('history/', views.history),
    path('register/', views.register_view),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('profile/', views.profile),
    path('admin-panel/', views.admin_panel),
    path(
        'ticket/<int:ticket_id>/',
        views.ticket_detail
    ),
    path(
        'ticket/<int:ticket_id>/update/',
        views.update_ticket_status
    ),
    path(
        'ticket/<int:ticket_id>/delete/',
        views.delete_ticket,
        name='delete_ticket'
    ),
    path(
    'verify-email/<uidb64>/<token>/',
    views.verify_email,
    name='verify_email'
    ),

]