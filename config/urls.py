"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings  # [DƏRS 10]
from django.conf.urls.static import static  # [DƏRS 10]
from django.contrib import admin
from django.urls import path, include  # [DƏRS 7] include əlavə etdik

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # [DƏRS 12]
    path('', include('blog.urls')),  # [DƏRS 7] qalan bütün ünvanlar blog/urls.py-a gedir
]

# [DƏRS 10] DEBUG rejimində media fayllarını Django özü göstərir (real serverdə bunu nginx edir)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
