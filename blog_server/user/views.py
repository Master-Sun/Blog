import hashlib
import json

from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.
from btoken.views import make_token
from tools.loging_decorator import loging_check
from user.models import UserProfile


# /v1/users
# /v1/users/<username>
# 装饰器：对指定的请求类型进行token校验
@loging_check('PUT')
def users(request, username=None):
    # 获取用户数据
    if request.method == 'GET':
        # /v1/users/kzzf?info=1  获取对象的对应属性---> {'info': 'xxx'}
        if username:
            # 具体用户的数据
            try:
                user = UserProfile.objects.get(username=username)
            except UserProfile.DoesNotExist:
                user = None
            if not user:
                result = {'code': 208, 'error': '用户不存在'}
                return JsonResponse(result)

            # 判断有无查询字符串
            if request.GET.keys():
                data = {}
                for k in request.GET.keys():
                    # 判断对象是否有此属性》》》》》》》》》》》》》》》》》
                    if hasattr(user, k):
                        data[k] = getattr(user, k)
                result = {'code': 200, 'username': username, 'data': data}
                return JsonResponse(result)
            else:
                # 没有查询字符串，返回前端需要的所有属性
                result = {'code': 200, 'username': username, 'data':
                # user.avatar拿到的是图片对象，str一下拿路径
                    {'info': user.info, 'sign': user.sign, 'nickname': user.nickname, 'avatar': str(user.avatar)}}
                return JsonResponse(result)

        else:
            # 查询全部用户的数据
            all_users = UserProfile.objects.all()
            res = []
            for user in all_users:
                d = dict()
                d['username'] = user.username
                d['email'] = user.email
                res.append(d)
            result = {'code': 200, 'data': res}
            return JsonResponse(result)

    # 注册用户
    elif request.method == 'POST':
        # 获取前端传递的json数据
        json_str = request.body
        if not json_str:
            # 前端异常提交：空数据
            result = {'code': 202, 'error': 'Please POST data'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        username = json_obj.get('username')
        email = json_obj.get('email')
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        if not username:
            result = {'code': 203, 'error': 'Please give me username'}
            return JsonResponse(result)
        if not email:
            result = {'code': 204, 'error': 'Please give me email'}
            return JsonResponse(result)
        if not password_1 or not password_2:
            result = {'code': 205, 'error': 'Please give me password'}
            return JsonResponse(result)
        if password_1 != password_2:
            result = {'code': 206, 'error': '两次密码不一致'}
            return JsonResponse(result)

        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code': 207, 'error': '用户名已存在'}
        hash_password = hashlib.sha1()
        hash_password.update(password_1.encode())
        try:
            UserProfile.objects.create(username=username, nickname=username, email=email,
                                       password=hash_password.hexdigest())
        except Exception as e:
            print('新用户创建失败，error=%s' % e)
            result = {'code': 207, 'error': '用户名已存在'}
            return JsonResponse(result)

        # 注册成功，生成token记录登陆状态
        token = make_token(username)
        result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}
        return JsonResponse(result)

    # 修改用户数据 /v1/users/<username>
    elif request.method == 'PUT':
        user = request.user
        json_str = request.body
        if not json_str:
            result = {'code': 202, 'error': '请上传数据'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        nickname = json_obj.get('nickname')
        if not nickname:
            result = {'code': 209, 'error': '昵称不能为空'}
            return JsonResponse(result)
        sign = json_obj.get('sign', '')
        info = json_obj.get('info', '')

        user.sign = sign
        user.info = info
        user.nickname = nickname
        user.save()
        result = {'code': 200, 'username': username}
        return JsonResponse(result)


@loging_check('POST')
def user_avatar(request, username):
    # 上传用户图片
    # 修改用户信息时，头像通过form表单的post请求进行单独提交
    # 由于目前django获取put类型请求的multipart的数据比较复杂
    # 因此此处改为post获取multipart数
    if not request.method == 'POST':
        result = {'code': 210, 'error': '请使用POST请求'}
        return JsonResponse(result)
    users = UserProfile.objects.filter(username=username)
    if not users:
        result = {'code': 208, 'error': '用户不存在'}
        return JsonResponse(result)
    if request.FILES.get('avatar'):
        users[0].avatar = request.FILES['avatar']
        users[0].save()
        result = {'code': 200, 'username': username}
        return JsonResponse(result)
    else:
        result = {'code': 211, 'error': '请上传头像'}
        return JsonResponse(result)