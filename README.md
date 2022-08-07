# microutil

简要：
基于django框架集成zookeeper分布式微服务的服务注册与发现工具包，方便HTTP远程调用


实现逻辑：
通过python的装饰器实现类，方法的自动注册到zookeeper上去，目前支持类注解，下面所有的方法均可注册到ZK。客户端通过服务发现去寻找具体的服务器地址，再通过HTTP调用方式获取相关的接口数据。


使用场景：
对于具有大量的后端服务之间的接口调用，类似于JAVA 之间的DUBBO接口调用一样，只不过这里使用的是HTTP 的方法，并没有使用DUBBO方式，也可以对于一些喜欢技术研究的人使用。


快速上手：


1. 安装插件包   

pip3 install microutil==1.0.2


2. 配置文件 setting.py 添加如下参数：

MICRO_ZK_HOST = '127.0.0.1'  # 必填  默认为 127.0.0.1

MICRO_ZK_PORT = 2181    # 必填 默认为 2181

MICRO_HTTP_PORT = 8000  # 必填  默认为 8000， python manage.py runserver 0.0.0.0:8000 这个地址为项目对外服务的端口，两者是一样的。

MICRO_SERVICE_NAME = 'micro'    # 必填 默认为 micro， 项目名称，全局唯一

MICRO_CLIENT_TIMEOUT = 10   # 选配 客户端调用超时配置 默认为 10S



3. 路由文件  urls.py 新增配置

from django.conf.urls import url
from microutil.server.site import jsonrpc_site

urlpatterns = [
    
    url(r'^json/', jsonrpc_site.dispatch, name='jsonrpc_mountpoint'),
]


4. 测试样例：（以下代码上面的项目中都有）

注册服务，提供者  http_views.py

from microutil.server.site import rpc


@rpc
def get_test(name):
    return name


@rpc
class HttpRpcService:

    @staticmethod
    def get_string(user_name, name, **kwargs):
        print(user_name, name, kwargs)
        return user_name

    @staticmethod
    def get_string_v1(name):
        print(name)
        return name


class HttpRpcServiceV:

    @staticmethod
    @rpc
    def get_string_v(user_name, name, **kwargs):
        print(user_name, name, kwargs)
        return name

调用服务，消费者  test_views.py


from django.http import JsonResponse
from microutil.server.proxy import HttpRpcClient

def get_test(request):
    res = HttpRpcClient.call('micro:HttpRpcService.get_string_v1', 'zhangsan')   #重点讲一下  第一个参数组成：项目名称:类名:方法名  或者 项目名称:方法名（针对于有的是方法级的注册）， 第二个参数为传值，
    print(res)
    ret = {
        'result': 1,
        'msg': '请求成功',
        'data': res
    }
    return JsonResponse(ret)
    
    
    
5. 以上的配置适应于本地开发和部署，如果要部署生产环境时则需要另外的预加载配置，样例使用uwsgi 部署

新增 apps.py 文件， 作用为uwsgi 启动的时候先要加载提供服务的方法。否则无法注册到zk.

from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'micro'  # app名称

    def ready(self):
        from micro.dubbo import http_views
        print('我被执行了！')

与上面同级目录下面 __init__.py, 新增下面的配置

default_app_config = 'micro.apps.MainConfig'


6. 以下代码在项目中均有，此处只是说明一下用处。


7. 使用过程中如果遇到了问题，可以联系作者本人：
加微信号：daqiangge2008


8. 项目借鉴了其它开源项目的部分代码和实现思想，非常感谢这些开源的前辈们。
