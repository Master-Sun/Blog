import json

from django.http import JsonResponse
from django.utils import timezone

from tools.loging_decorator import loging_check, get_user_by_request
from topic.models import Topic
from user.models import UserProfile


@loging_check('POST', 'DELETE')
def topics(request, author_id=None):
    # /v1/topics/<author_id>
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
        # 在纯文本内容中截取文章简介
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
        authors = UserProfile.objects.filter(username=author_id)
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

        # /v1/topics/kzzf?category=tec|no-tec  关键字查询
        category = request.GET.get('category')
        if category in ['tec', 'no-tec']:
            # 判断当前的访问者是否为博主
            if visitor_username == author_id:
                # 外键关联也可以直接使用id查询>>>>>>>>>>>>>>>>>>>>>>>???
                author_topics = Topic.objects.filter(author_id=author_id, category=category)
            else:
                # 其他访问者在访问当前博客
                author_topics = Topic.objects.filter(author_id=author_id, limit='public', category=category)
        else:
            # 判断当前的访问者是否为博主
            if visitor_username == author_id:
                # 外键关联可以使用对象，也可使用主键字段进行查询；filter的字段可以是author，也可以是author_id
                author_topics = Topic.objects.filter(author_id=author_id)
            else:
                # 其他访问者在访问当前博客
                author_topics = Topic.objects.filter(author_id=author_id, limit='public')

        res = make_topics_res(author, author_topics)
        return JsonResponse(res)

    # 删除博主的博客文章
    # /v1/topics/kzzf?topic_id=1
    elif request.method == 'DELETE':
        # 装饰器验证ok后会将登陆用户赋值给request.user，验证失败则抛出异常
        author = request.user
        # 删除时为保证万无一失，比对url中的username和token中的一致时方可执行删除
        if author.username != author_id:
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
