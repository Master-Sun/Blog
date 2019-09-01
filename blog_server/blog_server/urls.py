"""blog_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from .import views

urlpatterns = [
    url(r'^admin', admin.site.urls),
    url(r'^test_api$', views.test_api),
    url(r'v1/users', include('user.urls')),
    # 同于登陆操作，生成token，token好像是关键字，使用btoken
    url(r'v1/token', include('btoken.urls')),
    url(r'v1/topics', include('topic.urls')),
]

from django.conf.urls.static import static
from django.conf import settings
# 添加图片的路由映射
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
