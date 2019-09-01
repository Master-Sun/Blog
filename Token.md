## Token的生命周期

用户未登录

​	前端 肯定是没有token的

用户执行注册/登录 

​	1，一旦基础数据校验成功，后端生成token, 并且token包含此次注册/登录用户的用户名；并通过response返回给前端[json]

​	2，前端拿到response 的token后，将token存入到浏览器本地存储 ；方法如右：window.localStorage.setItem('dnblog', token)



用户每次访问博客页面【flask前端5000端口】

​	1，从本地存储中拿出token ,window.localStorage.getItem('dnblog')

​	2 ,  JS 将 token 放入 request 的 Authorization 头，发送http 请求向后端索要数据

​	3， 服务器-接到前端请求【当前URL 加了 loging_check,并且请求方法在 methods参数中】：

​			ex: loging_check('POST'), 则当前URL POST方法时进行如下校验

​				1，从 request Authorization 头 拿出token,

​				2，校验

​				3，校验不通过，返回前端异常码

​				4，校验通过，正常执行对应URL的视图函数

​	4，前端一旦接到 关于token的 异常码， 则删除本地存储中的token;

​		 且将用户转至登录界面