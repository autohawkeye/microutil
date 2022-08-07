from django.http import JsonResponse
from microutil.server.proxy import HttpRpcClient


def get_test(request):
    ret = {'user_name_1':'123', 'name_1':'lisi'}
    res = HttpRpcClient.call('micro:HttpRpcService.get_string_v1', 'zhangsan', 'name', **ret)
    print(res)
    ret = {
        'result': 1,
        'msg': '请求成功',
        'data': res
    }
    return JsonResponse(ret)