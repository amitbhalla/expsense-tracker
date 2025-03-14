from django.urls import path
from . import views

urlpatterns = [
    path('', views.account_list, name='account_list'),
    path('create/', views.account_create, name='account_create'),
    path('<int:pk>/update/', views.account_update, name='account_update'),
    path('<int:pk>/delete/', views.account_delete, name='account_delete'),
    
    path('types/', views.account_type_list, name='account_type_list'),
    path('types/create/', views.account_type_create, name='account_type_create'),
    path('types/<int:pk>/update/', views.account_type_update, name='account_type_update'),
    path('types/<int:pk>/delete/', views.account_type_delete, name='account_type_delete'),
]