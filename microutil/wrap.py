import functools
import socket


def retryTimes(retry_times=2):
    if retry_times <= 0:
        retry_times = 1
    
    def function(func):
        @functools.wraps(func)
        def wrapper(method_name, *args, **kwargs):
            lastEx = None
            for i in range(retry_times):
                try:
                    ret = func(method_name, *args, **kwargs)
                    return ret
                except socket.timeout as ex:
                    lastEx = ex
                except Exception as ex:
                    lastEx = ex
            raise lastEx
        return wrapper
    return function