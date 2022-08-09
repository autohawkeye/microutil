from kazoo.client import KazooClient
from django.conf import settings


class GlobalZkClient(object):

    zkClient = KazooClient(hosts=settings.MICRO_ZK_HOST + ':' + str(settings.MICRO_ZK_PORT))
    zkClient.start()