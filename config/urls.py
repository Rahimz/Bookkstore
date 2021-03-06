"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar


urlpatterns = [
    path('account/', include('account.urls')),
    path('files/', include('files.urls', namespace='files')),
    path('search/', include('search.urls', namespace='search')),
    path('staff/', include('staff.urls', namespace='staff')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('discounts/', include('discounts.urls', namespace='discounts')),
    path('zarinpal/', include('zarinpal.urls', namespace='zarinpal')),
    path('tools/', include('tools.urls', namespace='tools')),
    path('warehouses/', include('warehouses.urls', namespace='warehouses')),
    path('tickets/', include('tickets.urls', namespace='tickets')),
    path('rosetta/', include('rosetta.urls')),
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
    path('', include('shop.urls', namespace='shop')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
