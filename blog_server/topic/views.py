import json

from django.http import JsonResponse
from django.utils import timezone

from message.models import Message
from tools.loging_decorator import loging_check, get_user_by_request
from topic.models import Topic
from user.models import UserProfile


@loging_check('POST', 'DELETE')
def topics(request, username=None):
    # /v1/topics/<username>
    if request.method == 'POST':
        # 发表博客，必须为登陆状态
        # 验证token后会将user对象存入request
        author = request.user
        json_str = request.body
        if not json_str:
            result = {'code': 302, 'error': '请上传数据'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)

        title = json_obj.get('title')
        # 带html标签样式的内容
        content = json_obj.get('content')
        # 纯文本内容
        content_text = json_obj.get('content_text')
        # 在纯文本内容中截取文章简介>>>>>>>>>>>>>>>加一个简介的字段，而不用显示的时候进行中文截取
        introduce = content_text[:30]
        # 文章权限  public or private
        limit = json_obj.get('limit')
        if limit not in ['public', 'private']:
            # 判断权限是否合法
            result = {'code': 303, 'error': '权限类型错误'}
            return JsonResponse(result)
        # 文章种类  tec - 技术类   no-tec - 非技术类
        category = json_obj.get('category')
        if category not in ['tec', 'no-tec']:
            result = {'code': 303, 'error': '分类错误'}
            return JsonResponse(result)
        now = timezone.now()

        Topic.objects.create(title=title, content=content, limit=limit, category=category,
                             author=author, created_time=now, modified_time=now,
                             introduce=introduce)
        result = {'code': 200, 'username': author.username}
        return JsonResponse(result)

    # 获取用户博客列表 或 具体博客的内容( ?t_id=xx)
    # /v1/topics/kzzf
    elif request.method == 'GET':
        # 获取当前访问的博客的博主
        authors = UserProfile.objects.filter(username=username)
        if not authors:
            result = {'code': 305, 'error': '博主不存在'}
        author = authors[0]

        # 获取当前访问者 visitor，已登陆或未登录
        visitor = get_user_by_request(request)
        visitor_username = None
        # 比对 author和visitor的username，判断访问者是否为博主
        # 是博主则返回所有博客，否则返回权限为public的博客
        if visitor:
            # 访问者已登陆，获取用户名
            visitor_username = visitor.username

        # /v1/topics/kzzf?t_id=1
        # 如果有t_id，则当前请求是获取博主指定id的博客
        t_id = request.GET.get('t_id')
        if t_id:
            # 访问者是否为博主的标记
            is_self = False
            if visitor_username == username:
                is_self = True
                try:
                    author_topic = Topic.objects.get(id=t_id)
                except Exception as e:
                    result = {'code': 309, 'error': '博客不存在'}
                    return JsonResponse(result)
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id, limit='public')
                except Exception as e:
                    result = {'code': 309, 'error': '博客不存在'}
                    return JsonResponse(result)
            res = make_topic_res(author, author_topic, is_self)
            return JsonResponse(res)
        else:
            # 没有t_id时 即为查询有所博客
            # /v1/topics/kzzf?category=tec|no-tec  关键字查询
            category = request.GET.get('category')
            if category in ['tec', 'no-tec']:
                # 判断当前的访问者是否为博主
                if visitor_username == username:
                    # 外键关联的是主键，user表中设置username为主键了，表中没有id字段
                    author_topics = Topic.objects.filter(author=username, category=category)
                else:
                    # 其他访问者只能访问pubilc类型的博客
                    author_topics = Topic.objects.filter(author=username, limit='public', category=category)
            else:
                # 判断当前的访问者是否为博主
                if visitor_username == username:
                    # 外键关联可以使用对象，也可使用主键字段进行查询；filter的字段可以是author，也可以是author_id
                    author_topics = Topic.objects.filter(author_id=username)
                else:
                    # 其他访问者在访问当前博客
                    author_topics = Topic.objects.filter(author_id=username, limit='public')

            res = make_topics_res(author, author_topics)
            return JsonResponse(res)

    # 删除博主的博客文章
    # /v1/topics/kzzf?topic_id=1
    elif request.method == 'DELETE':
        # 装饰器验证ok后会将登陆用户赋值给request.user，验证失败则抛出异常
        author = request.user
        # 删除时为保证万无一失，比对url中的username和token中的一致时方可执行删除
        if author.username != username:
            result = {'code': 306, 'error': '不能执行'}
            return JsonResponse(result)

        # DELETE请求也可通过GET取参数》》》》》》》》》
        topic_id = request.GET.get('topic_id')
        if not topic_id:
            result = {'code': 307, 'error': '你不能这么做'}
            return JsonResponse(result)

        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            print('博客删除错误：%s' % e)
            result = {'code': 308, 'error': '博客不存在'}
            return JsonResponse(result)

        topic.delete()
        return JsonResponse({'code': 200})


def make_topics_res(author, author_topics):
    res = {'code': 200, 'data': {}}
    topics_res = []
    for topic in author_topics:
        d = dict()
        d['id'] = topic.id
        d['title'] = topic.title
        d['category'] = topic.category
        d['created_time'] = topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
        d['introduce'] = topic.introduce
        d['author'] = author.nickname
        topics_res.append(d)
    res['data']['topics'] = topics_res
    res['data']['nickname'] = author.nickname
    return res


def make_topic_res(author, author_topic, is_self):
    """
    生成博客详情页的返回值
    :param author:
    :param author_topic:
    :return:
    """
    if is_self:
        # next 下一篇博客：大于当前博客id的下一个  博主的博客
        next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author.username).first()
        # 取出上一篇博客，取出的结果默认是按id从小大大排的，所以这里用last方法取最后一个
        last_topic = last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author).last()
    else:
        next_topic = Topic.objects.filter(
            id__gt=author_topic.id,
            limit='public',
            author=author.username).first()
        last_topic = Topic.objects.filter(
            id__gt=author_topic.id,
            limit='public',
            author=author.username).last()

    # 处理返回前端的数据
    if next_topic:
        next_id = next_topic.id
        next_title = next_topic.title
    else:
        next_id = None
        next_title = None
    if last_topic:
        last_id = last_topic.id
        last_title = last_topic.title
    else:
        last_id = None
        last_title = None

    result = {'code': 200, 'data': {}}
    result['data']['nickname'] = author.nickname
    result['data']['title'] = author_topic.title
    result['data']['category'] = author_topic.category
    result['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d')
    result['data']['content'] = author_topic.content
    result['data']['introduce'] = author_topic.introduce
    result['data']['author'] = author.nickname
    result['data']['next_id'] = next_id
    result['data']['next_title'] = next_title
    result['data']['last_id'] = last_id
    result['data']['last_title'] = last_title

    # 生成message留言信息
    # 倒序拿出所有的留言对象
    all_messages = Message.objects.filter(topic=author_topic).order_by('-id')
    msg_list = []  # 里面放字典，存入留言以及对应的回复
    level_msg = {}    # key:留言id；value：回复对象[]
    for msg in all_messages:
        if msg.parent_message == 0:
            # 留言
            msg_list.append({'id': msg.id, 'content': msg.content,
                             'publisher': msg.publisher.nickname,
                             # ImageField字段拿到的是一个对象，__str__方法可返回字符串路径，方便后续转json
                             'publisher_avatar': str(msg.publisher.avatar),
                             'created_time': msg.created_time.strftime("%Y-%m-%d"),
                             'reply': []})
        else:
            # 回复
            # setdefault：设置key的默认值，key不存在时生效>>>>>>>>>
            level_msg.setdefault(msg.parent_message, [])
            level_msg[msg.parent_message].append({'msg_id': msg.id,
                                                  'publisher': msg.publisher.nickname,
                                                  'publisher_avatar': str(msg.publisher.avatar),
                                                  'content': msg.content,
                                                  'created_time': msg.created_time.strftime('%Y-%m-%d'),
                                                  })
        # 关联留言和回复
        for m in msg_list:
            if m['id'] in level_msg:
                m['reply'] = level_msg[m['id']]

    result['data']['messages'] = msg_list  # 暂未处理留言问题
    result['data']['messages_count'] = len(all_messages)
    return result
