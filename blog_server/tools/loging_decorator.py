import jwt
from django.http import JsonResponse

from user.models import UserProfile


KEY = 'abcdef1234'


# *methods：可接受任意参数
# 最外层的函数是为了给装饰器传参
def loging_check(*methods):
    def _loging_check(func):
        def wrapper(request, *args, **kwargs):
            # token 放在 request header authorization
            token = request.META.get('HTTP_AUTHORIZATION')
            if not methods:
                # 如果没传methods参数，则直接返回视图
                return func(request, *args, **kwargs)
            # 如果当前请求的方法不在methods内，则直接返回视图
            if request.method not in methods:
                return func(request, *args, **kwargs)

            # 前端没有token时，传过来的可能是空或者'null'，此处要根据实际清空进行判断
            if not token or token == 'null':
                result = {'code': 107, 'error': '请上传token'}
                return JsonResponse(result)
            # 校验token，pyjwt注意 异常检测
            try:
                res = jwt.decode(token, KEY, algorithms='HS256')
            except jwt.ExpiredSignatureError:
                # token过期
                result = {'code': 108, 'error': '请登录'}
                return JsonResponse(result)
            except Exception as e:
                # token错误
                result = {'code': 108, 'error': '请登录'}
                return JsonResponse(result)

            # 校验成功则根据用户名取出用户(前端传递的用户名有错误的风险，此处以token中的为准)
            username = res['username']
            user = UserProfile.objects.get(username=username)
            # request.user = user   取出的用户直接赋给request.user
            request.user = user
            return func(request, *args, **kwargs)
        return wrapper
    return _loging_check


def get_user_by_request(request):
    """
    通过request获取用户
    :param request:
    :return: user对象 或者 None
    """
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token or token == 'null':
        return None
    try:
        res = jwt.decode(token, KEY, algorithms='HS256')
    except Exception as e:
        print('=== get_user_by_request ==jwt decode error %s' % e)
        return None
    # 获取token中的用户名
    username = res['username']

    user = UserProfile.objects.get(username=username)
    return user
