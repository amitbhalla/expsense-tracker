from django.contrib import admin
from django.urls import path, include
from dashboard.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('transactions/', include('transactions.urls')),
    path('dashboard/', include('dashboard.urls')),
]