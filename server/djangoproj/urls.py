from django.contrib import admin
from django.http import FileResponse
from django.urls import include, path, re_path
from django.conf import settings


def frontend(request):
    return FileResponse(open(settings.BASE_DIR / 'frontend/build/index.html', 'rb'), content_type='text/html')


def about(request):
    return FileResponse(open(settings.BASE_DIR / 'frontend/static/About.html', 'rb'), content_type='text/html')


def contact(request):
    return FileResponse(open(settings.BASE_DIR / 'frontend/static/Contact.html', 'rb'), content_type='text/html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('djangoapp/', include('djangoapp.urls')),
    path('about', about),
    path('contact', contact),
    re_path(r'^(?:|login/?|register/?|dealer/\d+/?|postreview/\d+/?)$', frontend),
]
