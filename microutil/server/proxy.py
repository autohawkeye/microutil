import uuid

from six.moves.urllib import request as urllib_request
from six.moves.urllib import error as urllib_error
from microutil.server.serialize import BinarySerialize
from microutil.compress import Compress
from microutil._json import loads, dumps
from microutil.server.zookeeper import ZKClient
from microutil.wrap import retryTimes
from microutil.md5 import Md5
from django.conf import settings


class HttpRpcClient(object):

    @staticmethod
    @retryTimes(retry_times=3)
    def call(method_name, *args, **kwargs):
        if len(method_name.split(':')) != 2:
            raise Exception('方法名称格式不正确，格式应为<服务名:方法名>')
        method_name_l = method_name.split(':')[1]
        service_name = method_name.split(':')[0]
        request_id = str(uuid.uuid1())
        data = dumps(
            {
                'version': '1.0',
                'method': method_name_l,
                'args': args,
                'kwargs': kwargs,
                'request_id': request_id
            }
        ).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Content-Length': len(data),
            'micro-request-id': request_id
        }
        if hasattr(settings, 'MICRO_REMOTE_SERVER_AUTHENTICATION_TOKEN'):
            remote_tokens = settings.MICRO_REMOTE_SERVER_AUTHENTICATION_TOKEN
            if remote_tokens.get(service_name):
                headers['micro-auth-token'] = Md5.get_md5_str(3 * (remote_tokens.get(service_name) + request_id))
            else:
                headers['micro-auth-token'] = Md5.get_md5_str(3 * (2 * 'micro' + request_id))
        else:
            headers['micro-auth-token'] = Md5.get_md5_str(3 * (2 * 'micro' + request_id))
        try:
            zk_client = ZKClient()
            service_ip, service_port = zk_client.get_connection(method_name)
            req = urllib_request.Request('http://' + service_ip + ':' + str(service_port) + '/jsonp/', data, headers)
            if hasattr(settings, 'MICRO_CLIENT_TIMEOUT'):
                time_out = settings.MICRO_CLIENT_TIMEOUT
            else:
                time_out = 10
            resp = urllib_request.urlopen(req, timeout=time_out)
        except IOError as e:
            if isinstance(e, urllib_error.HTTPError):
                if e.code not in (
                        401, 403
                ) and e.headers['Content-Type'] == 'application/json-rpc':
                    return e.read().decode('utf-8')  # we got a jsonrpc-formatted respnose
                raise ServiceProxyException(e.code, e.headers, req)
            else:
                raise e
        data = resp.read()
        if data == b'':
            raise Exception('peer closed')
        bin_data = data[1:]
        compressField = data[:1]
        isEnableCompress = 0
        if compressField == b'1':
            isEnableCompress = 1
        if isEnableCompress:
            resp_dict = loads(BinarySerialize.unserialize(Compress.decompress(bin_data)))
        else:
            resp_dict = loads(BinarySerialize.unserialize(bin_data))
        if resp_dict.get('error'):
            print(resp_dict)
        else:
            return resp_dict.get('result')


class ServiceProxyException(IOError):
    def __init__(self, code, headers, request):
        self.args = ('An Error Occurred', code, headers, request)
        self.code = code
        self.message = 'An Error Occurred'
        self.headers = headers
        self.request = request