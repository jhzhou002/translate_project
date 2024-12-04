from django.urls import path
from translate_app import views

urlpatterns = [
    path('', views.translate_view, name='translate_view'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]