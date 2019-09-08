from django.conf.urls import url
from .import views

urlpatterns = [
    # /v1/topics/username
    url(r'^/(?P<topic_id>[\d]+)$', views.messages, name='messages'),
]