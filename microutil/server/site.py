from uuid import uuid1
from microutil._json import loads, dumps
from microutil.md5 import Md5
from microutil.server.method import RpcMethod
from microutil.server import GlobalZkClient
from microutil.server.serialize import BinarySerialize
from microutil.server.compress import RpcCompress
from microutil.compress import Compress
from microutil.exceptions import *

from microutil.exceptions import FuncNotFoundException
from django.conf import settings
from types import FunctionType
import inspect

empty_dec = lambda f: f
try:
    from django.views.decorators.csrf import csrf_exempt
except (NameError, ImportError):
    csrf_exempt = empty_dec

from django.core.serializers.json import DjangoJSONEncoder


class HttpRpcSite(object):
    "A JSON-RPC Site"

    funcMap = {}
    funcList = []

    def __init__(self, json_encoder=DjangoJSONEncoder):
        self.zk_host = None
        self.url = {}
        self.uuid = str(uuid1())
        self.version = '1.0'
        self.name = 'django-json-rpc'
        self.set_json_encoder(json_encoder)

    def set_json_encoder(self, json_encoder=DjangoJSONEncoder):
        self.json_encoder = json_encoder

    def empty_response(self, version='1.0'):
        resp = {'request_id': None}
        resp.update({'error': None, 'result': None})
        return resp

    def run(self, func, args, kwargs):
        try:
            if func not in self.funcList:
                return FuncNotFoundException('func not found')
            methodObj = self.funcMap[func]
            args = tuple(args)
            if len(args) == 0 and len(kwargs) == 0:
                resp = methodObj.call()
            else:
                resp = methodObj.call(*args, **kwargs)
            return resp
        except Exception as ex:
            return Exception('server exception, ' + str(ex))

    @csrf_exempt
    def dispatch(self, request, method='', json_encoder=None):
        from django.http import HttpResponse
        json_encoder = json_encoder or self.json_encoder
        try:
            # in case we do something json doesn't like, we always get back valid json-rpc response
            response = self.empty_response()
            if request.method.lower() == 'get':
                raise InvalidRequestError('The method not support GET requests')
            elif not request.method.lower() == 'post':
                raise RequestPostError
            else:
                try:
                    if hasattr(request, "body"):
                        req = loads(request.body.decode('utf-8'))
                    else:
                        req = loads(request.raw_post_data.decode('utf-8'))
                    micro_request_id = request.META.get('HTTP_MICRO_REQUEST_ID')
                    auth_token = request.META.get('HTTP_MICRO_AUTH_TOKEN')
                    if hasattr(settings, 'MICRO_SERVER_AUTHENTICATION_TOKEN'):
                        server_token = settings.MICRO_SERVER_AUTHENTICATION_TOKEN
                        if server_token:
                            check_auth_token = Md5.get_md5_str(3 * (server_token + micro_request_id))
                        else:
                            check_auth_token = Md5.get_md5_str(3 * (2 * 'micro' + micro_request_id))
                    else:
                        check_auth_token = Md5.get_md5_str(3 * (2 * 'micro' + micro_request_id))
                    if check_auth_token != auth_token:
                        return HttpResponse('认证信息为空或错误', status=401, content_type='application/json-rpc')
                except:
                    raise InvalidRequestError

                resp = self.run(req['method'], req['args'], req['kwargs'])
                response['result'] = resp
                response['request_id'] = req['request_id']
                status = 200
            json_rpc = dumps(response, cls=json_encoder)
        except Error as e:
            response['error'] = e.json_rpc_format
            status = e.status
            json_rpc = dumps(response, cls=json_encoder)
        except Exception as e:
            if settings.DEBUG:
                other_error = OtherError(e)
            else:
                other_error = OtherError("Internal Server Error")
            response['result'] = None
            response['error'] = other_error.json_rpc_format
            status = other_error.status
            json_rpc = dumps(response, cls=json_encoder)
        bin_serialize = BinarySerialize.serialize(json_rpc)
        if len(bin_serialize) > RpcCompress.enableCompressLen:
            bin_serialize = b'1' + Compress.compress(bin_serialize)
        else:
            bin_serialize = b'0' + bin_serialize
        return HttpResponse(bin_serialize,
                            status=status,
                            content_type='application/json-rpc')

    @classmethod
    def rpc(cls, func):
        cls.regist(func)
        return func

    @classmethod
    def regist(cls, func):
        if isinstance(func, FunctionType):
            if inspect.iscoroutinefunction(func):
                cls.funcMap[func.__name__] = RpcMethod(RpcMethod.TYPE_WITHOUT_CLASS, func, isCoroutine=True)
                cls.funcList = cls.funcMap.keys()
            else:
                cls.funcMap[func.__name__] = RpcMethod(RpcMethod.TYPE_WITHOUT_CLASS, func)
                cls.funcList = cls.funcMap.keys()
        else:
            classDefine = func
            serMethods = list(filter(lambda m: not m.startswith('_'), dir(classDefine)))
            for methodName in serMethods:
                funcName = "{}.{}".format(classDefine.__name__, methodName)
                funcObj = getattr(classDefine, methodName)
                if inspect.iscoroutinefunction(funcObj):
                    cls.funcMap[funcName] = RpcMethod(RpcMethod.TYPE_WITH_CLASS, funcObj, classDefine, isCoroutine=True)
                    cls.funcList = cls.funcMap.keys()
                else:
                    cls.funcMap[funcName] = RpcMethod(RpcMethod.TYPE_WITH_CLASS, funcObj, classDefine)
                    cls.funcList = cls.funcMap.keys()


rpc = HttpRpcSite.rpc
jsonrpc_site = HttpRpcSite()
