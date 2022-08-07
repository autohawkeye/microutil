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
