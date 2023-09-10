
from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from todolist import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include(('apps.core.urls', 'apps.core'))),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('goals/', include(('apps.goals.urls', 'apps.goals'))),
    path('bot/', include(('apps.bot.urls', 'apps.bot'))),

    path('docs/schema', SpectacularAPIView.as_view(), name='schema'),
    path('docs/swagger', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger')
]

if settings.DEBUG:
    urlpatterns += [
        path('api-auth/', include('rest_framework.urls')),
    ]
