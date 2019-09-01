import hashlib
import json, jwt, time

from django.http import JsonResponse
from django.shortcuts import render

from user.models import UserProfile


# Create your views here.
def make_token(username, expire=3600*24):
    '''
    生成token
    :param username:
    :param expire:
    :return:
    '''
    key = 'abcdef1234'
    now_t = time.time()
    payload = {'username': username, 'exp': int(now_t)+expire}
    # pip install pyjwt
    return jwt.encode(payload, key, algorithm='HS256')


def btoken(request):
    if not request.method == 'POST':
        result = {'code': 101, 'error': '请使用POST请求'}
        return JsonResponse(result)

    # 获取提交的数据
    json_str = request.body
    if not json_str:
        result = {'code': 102, 'error': '请上传数据'}
        return JsonResponse(result)

    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    password = json_obj.get('password')
    if not username:
        result = {'code': 103, 'error': '请上传用户名'}
        return JsonResponse(result)
    if not password:
        result = {'code': 104, 'error': '请上传密码'}
        return JsonResponse(result)

    users = UserProfile.objects.filter(username=username)
    if not users:
        result = {'code': 105, 'error': '用户名或密码错误'}
        return JsonResponse(result)

    # hash password
    p_m = hashlib.sha1()
    p_m.update(password.encode())
    if p_m.hexdigest() != users[0].password:
        result = {'code': 106, 'error': '用户名或密码错误'}
        return JsonResponse(result)

    # 生成token
    token = make_token(username)
    result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}
    return JsonResponse(result)

