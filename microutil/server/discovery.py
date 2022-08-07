import json
from kazoo.client import KazooClient
from django.conf import settings


# TCP服务端绑定端口开启监听，同时将自己注册到zk
class ZkRpcDiscovery(object):
    __slots__ = ('host', 'port', 'service_name', 'service_host', 'service_port', 'zk')

    def __init__(self, host, port, service_name, service_host, service_port):
        self.host = host
        self.port = port
        self.service_name = service_name
        self.service_host = service_host
        self.service_port = service_port
        self.zk = KazooClient(hosts=host + ':' + str(port))
        self.zk.start()

    def register_zk(self):
        """
        注册到zookeeper
        """
        if hasattr(settings, 'MICRO_SERVICE_NAME'):
            micro_service_name = settings.MICRO_SERVICE_NAME
        else:
            micro_service_name = 'micro'
        value = json.dumps({'host': self.service_host, 'port': self.service_port})
        # 创建服务子节点
        self.zk.create('/dubbo/' + micro_service_name + '/' + self.service_name + '/provider/', value.encode(), ephemeral=True, sequence=True, makepath=True)
