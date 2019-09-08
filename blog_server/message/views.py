import json

from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.
from django.utils import timezone

from message.models import Message
from tools.loging_decorator import loging_check
from topic.models import Topic


@loging_check('POST')
def messages(request, topic_id):
    """
    获取博客的留言和回复
    :param request:
    :param topic_id:
    :return:
    """
    if request.method == 'POST':
        # 创建留言/回复
        user = request.user
        json_str = request.body
        if not json_str:
            result = {'code': 402, 'error': '请提交数据'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        content = json_obj.get('content')
        # 父级留言的id
        parent_id = json_obj.get('parent_id', 0)
        if not content:
            result = {'code': 403, 'error': '请提交留言'}
            return JsonResponse(result)
        now = timezone.now()
        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            result = {'code': 404, 'error': '博客不存在'}
            return JsonResponse(result)

        if topic.limit == 'private':
            # 私密博客，校验是否为博主
            if user.username != topic.author.username:
                result = {'code': 405, 'error': '没有权限'}
                return JsonResponse(result)
        Message.objects.create(topic=topic, content=content,
               parent_message=parent_id, created_time=now, publisher=user)
        return JsonResponse({'code': 200, 'data': {}})


