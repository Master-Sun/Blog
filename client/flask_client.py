# -*- coding:utf-8 -*-
 ######################################################
#        > File Name: flask_client.py
#      > Author: GuoXiaoNao
 #     > Mail: 250919354@qq.com 
 #     > Created Time: Mon 20 May 2019 11:52:00 AM CST
 ######################################################

from flask import Flask, send_file

# flask默认静态文件目录：根目录下的static
# flask默认模板文件目录：根目录下的templates

# 初始化Flask
app = Flask(__name__)


# 绑定路由url和执行函数
@app.route('/index')
def index():
    # 首页
    # send_file：直接返回具体的页面
    return send_file('templates/index.html')


@app.route('/login')
def login():
    # 登录
    return send_file('templates/login.html')


@app.route('/register')
def register():
    # 注册
    return send_file('templates/register.html')


@app.route('/<username>/info')
def info(username):
    # 个人信息
    return send_file('templates/about.html')


@app.route('/<username>/change_info')
def change_info(username):
    #修改个人信息
    return send_file('templates/change_info.html')


@app.route('/<username>/topic/release')
def topic_release(username):
    # 发表博客
    return send_file('templates/release.html')


@app.route('/<username>/topics')
def topics(username):
    # 个人博客列表
    return send_file('templates/list.html')


@app.route('/<username>/topics/detail/<t_id>')
def topics_detail(username, t_id):
    # 博客内容详情
    return send_file('templates/detail.html')


@app.route('/test')
def test():
    return send_file('templates/test.html')


if __name__ == '__main__':
    # 启动flask服务，debug参数-True 则进入调试模式
    # 启动命令：python 文件名；默认监听5000端口
    app.run(debug=True)

