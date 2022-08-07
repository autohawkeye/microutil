import random
import time
import json
import socket
from kazoo.client import KazooClient
from django.conf import settings


class GlobalObject(object):
    node_servers = {}
    try:
        if hasattr(settings, 'MICRO_ZK_HOST'):
            zk_host = settings.MICRO_ZK_HOST
        else:
            zk_host = '127.0.0.1'
        if hasattr(settings, 'MICRO_ZK_PORT'):
            zk_port = settings.MICRO_ZK_PORT
        else:
            zk_port = 2181
        zk = KazooClient(hosts=zk_host + ':' + str(zk_port))
        zk.start()
    except Exception as e:
        pass


class ZKClient(object):

    def __init__(self):
        self._count = 0

    def _my_func(self, event):
        GlobalObject.node_servers = {}

    def _get_servers(self, service_name, event=None):
        """
        从zookeeper获取服务器地址信息列表
        """
        serv = service_name.split(':')[0]
        service_name = service_name.split(':')[1]
        servers = GlobalObject.zk.get_children('/dubbo/' + serv + '/' + service_name + '/provider/', watch=self._my_func)
        server_list = []
        for server in servers:
            data = GlobalObject.zk.get('/dubbo/' + serv + '/' + service_name + '/provider/' + server)[0]
            if data:
                addr = json.loads(data.decode())
                server_list.append(addr)
        GlobalObject.node_servers[serv] = server_list

    def _get_server(self, service_name):
        """
        随机选出一个可用的服务器
        """
        serv = service_name.split(':')[0]
        if not GlobalObject.node_servers.get(serv):
            self._get_servers(service_name)
        print(GlobalObject.node_servers.get(serv))
        return random.choice(GlobalObject.node_servers.get(serv))

    def get_connection(self, service_name):
        """
        提供一个可用的tcp连接
        """
        service_ip = None
        service_port = None
        while True:
            server = self._get_server(service_name)
            print('server:%s' % server)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((server['host'], server['port']))
                service_ip = server['host']
                service_port = server['port']
            except ConnectionRefusedError:
                time.sleep(1)
                continue
            else:
                break
        return service_ip, service_port