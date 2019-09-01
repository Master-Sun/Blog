from django.conf.urls import url
from . import views


urlpatterns = [
    # 获取用户列表，跟下面共用一个视图处理函数，通过请求类型区分
    url(r'^$', views.users, name='users'),
    # 获取一个用户的信息
    url(r'^/(?P<username>[\w]{4,11})$', views.users, name='user'),
    # /v1/users/kzzf/avatar  修改用户头像
    url(r'^/(?P<username>[\w]{4,11})/avatar$', views.user_avatar, name='user_avatar'),
]