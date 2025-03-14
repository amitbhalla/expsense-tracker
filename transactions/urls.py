from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('create/', views.transaction_create, name='transaction_create'),
    path('<int:pk>/update/', views.transaction_update, name='transaction_update'),
    path('<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    path('transfer/', views.create_transfer, name='create_transfer'),
    path('export/csv/', views.export_transactions_csv, name='export_transactions_csv'),
    path('import/csv/', views.import_transactions_csv, name='import_transactions_csv'),
    path('download/template/', views.download_csv_template, name='download_csv_template'),
]